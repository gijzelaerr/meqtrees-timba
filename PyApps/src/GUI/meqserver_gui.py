#!/usr/bin/python

from Timba.dmi import *
from Timba.GUI.app_proxy_gui import *
from Timba.GUI.pixmaps import pixmaps
from Timba.Meq import meqds
from Timba.GUI.browsers import *
from Timba.GUI import treebrowser
from Timba.GUI.procstatuswidget import *
from Timba.GUI import meqgui 
from Timba.GUI import bookmarks 
from Timba import Grid

import weakref
import math
import sets
import re

_dbg = verbosity(0,name='meqserver_gui');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

makeNodeDataItem = meqgui.makeNodeDataItem;

# global symbol: meqserver object; initialized when a meqserver_gui
# is constructed
mqs = None;

class NodeBrowser(HierBrowser,GriddedPlugin):
  _icon = pixmaps.treeviewoblique;
  viewer_name = "Node Browser";
  
  def __init__(self,gw,dataitem,cellspec={},default_open=None,**opts):
    GriddedPlugin.__init__(self,gw,dataitem,cellspec=cellspec);
    HierBrowser.__init__(self,self.wparent(),"value","field",
        udi_root=(dataitem and dataitem.udi));
    self.set_cell_content(self.wtop(),dataitem.caption,icon=self.icon());
    # parse the udi
    (name,ni) = meqds.parse_node_udi(dataitem.udi);
    if ni is None:
      node = meqds.nodelist[name or dataitem.data.name];
    else:
      node = meqds.nodelist[ni];
    self._default_open = default_open;
    self._state = None;
    # at this point, _node is a very basic node record: all it has is a list
    # of children nodeindices, to which we'll dispatch update requests
    # construct basic view items
    lv = self.wlistview();
    self.set_udi_root(dataitem.udi);
    # Node state
    self._item_state = HierBrowser.Item(lv,'Current state','',udi=dataitem.udi,udi_key='state');
    # Node children
    # note that dataitem.data may be a node state or a node stub record,
    # depending on whether it is already available to us, so just to make sure
    # we always go back to meqds for the children list
    if len(node.children):
      childroot = HierBrowser.Item(lv,'Children (%d)'%len(node.children),'',udi_key='child');
      self._child_items = {};
      for (cid,child) in node.children: 
        # this registers out callback for whenever a child's state is sent over
        meqds.subscribe_node_state(child,self.set_child_state);
        # this initiates a state request for the child
        meqds.request_node_state(child);
        # create a listview item for that child
        self._child_items[child] = HierBrowser.Item(childroot,str(cid),'#'+str(child));
    else:
      self._child_items = None;
    # State snapshots
    meqds.subscribe_node_state(ni,self.set_own_state);
    sslist = meqds.get_node_snapshots(ni);
    self._item_snapshots = HierBrowser.Item(lv,'','',udi_key='snapshot');
    self._last_snapshot = None;
    nss = 0;
    for (stateref,event,timestamp) in sslist:
      st = stateref();
      if st is not None:
        item = HierBrowser.Item(self._item_snapshots, \
                time.strftime('%H:%M:%S',time.localtime(timestamp)),\
                str(event),udi_key=str(nss));
        item.cache_content(st);
        nss += 1;
    self._item_snapshots.setText(0,'Snapshots (%d)'%nss);
    # If we already have a full state record, go use it
    # Note that this will not always be the case; in the general case,
    # the node state will arrive later (perhaps even in between child
    # states)
    if dataitem.data is not None:
      self.set_data(dataitem);
    lv.setCurrentItem(None);

  # our own state is added to snapshots here (and to the main view
  # in set_data below)
  def set_own_state (self,state,event):
    if state is self._last_snapshot or getattr(state,'__nochange',False):
      return;
    # add snapshot
    nss = self._item_snapshots.childCount();
    item = HierBrowser.Item(self._item_snapshots, \
           time.strftime('%H:%M:%S'),str(event),udi_key=str(nss));
    item.cache_content(state);
    self._last_snapshot = state;
    # change label on snapshots item
    self._item_snapshots.setText(0,'Snapshots (%d)'%(nss+1));
      
  # this callback is registered for all child node state updates
  def set_child_state (self,node,event):
    _dprint(3,'Got state for child',node.name,node.field_names());
    _dprint(3,'Event is',event);
    if not self._child_items:
      raise RuntimeError,'no children expected for this node';
    item = self._child_items.get(node.nodeindex,None);
    if not item:
      raise ValueError,'this is not our child';
    # store node name in item
    item.setText(2,"%s (%s)"%(node.name,node['class'].lower()));
    item.set_udi(meqds.node_udi(node));
    self.change_item_content(item,node,\
      make_data=curry(makeNodeDataItem,node));
    
  def set_data (self,dataitem,default_open=None,**opts):
    # open items (use default first time round)
    openitems = default_open or self._default_open;
    if self._state is not None:
      # do nothing if state has already been marked as unchanged
      if getattr(dataitem.data,'__nochange',False):
        return;
      # if something is already open, use that
      openitems = self.get_open_items() or openitems;
    # at this point, dataitem.data is a valid node state record
    _dprint(3,'Got state for node',dataitem.data.name,dataitem.data.field_names());
    self.change_item_content(self._item_state,dataitem.data,viewable=False);
    # apply saved open tree
    self.set_open_items(openitems);
    self._state = dataitem.data;
    
class meqserver_gui (app_proxy_gui):

  StatePixmaps = { None: pixmaps.stop, \
    treebrowser.AppState.Idle: pixmaps.grey_cross,
    treebrowser.AppState.Stream: pixmaps.spigot,
    treebrowser.AppState.Debug: pixmaps.breakpoint };

  def __init__(self,app,*args,**kwargs):
    meqds.set_meqserver(app);
    global mqs;
    self.mqs = mqs = app;
    self.mqs.track_results(False);
    # init standard proxy GUI
    app_proxy_gui.__init__(self,app,*args,**kwargs);
    # add handlers for various application events
    self._add_ce_handler("node.result",self.ce_NodeResult);
    self._add_ce_handler("process.status",self.ce_ProcessStatus);
    self._add_ce_handler("app.result.node.get.state",self.ce_NodeState);
    self._add_ce_handler("app.result.get.node.list",self.ce_LoadNodeList);
    self._add_ce_handler("app.update.status.num.tiles",self.ce_UpdateAppStatus);
    
  def populate (self,main_parent=None,*args,**kwargs):
    # init icons
    pixmaps.load_icons('treebrowser');
    # populate GUI
    app_proxy_gui.populate(self,main_parent=main_parent,*args,**kwargs);
    self.setIcon(pixmaps.trees48x48.pm());
    self.set_verbose(self.get_verbose());
    
    _dprint(2,"meqserver-specifc init"); 
    # add Tree browser panel
    self.treebrowser = treebrowser.TreeBrowser(self);
    self.add_tab(self.treebrowser.wtop(),"Trees",index=1);
    self.connect(self.treebrowser.wtop(),PYSIGNAL("view_node()"),self._view_node);
    self.connect(self.treebrowser.wtop(),PYSIGNAL("view_forest_state()"),self._view_forest_state);
    
    # add Result Log panel
    self.resultlog = Logger(self,"node snapshot log",limit=1000,scroll=False,
          udi_root='snapshot');
    self.resultlog.wtop()._newres_iconset  = pixmaps.check.iconset();
    self.resultlog.wtop()._newres_label    = "Snapshots";
    self.resultlog.wtop()._newresults      = False;
    self.add_tab(self.resultlog.wtop(),"Snapshots",index=2);
    QObject.connect(self.resultlog.wlistview(),PYSIGNAL("displayDataItem()"),self.display_data_item);
    QObject.connect(self.maintab,SIGNAL("currentChanged(QWidget*)"),self._reset_resultlog_label);
    
    # excluse ubiquotous events from the event logger
    self.eventlog.set_mask('!node.status.*;!process.status;'+self.eventlog.get_mask());
    
    # add dummy stretch, and a memory size widget
    self._wstat = ProcStatusWidget(self.statusbar);
    self._wstat.hide();
    dum = QWidget(self.statusbar);
    self.statusbar.addWidget(dum,10);
    self.statusbar.addWidget(self._wstat,0);
    
    # build menu bar
    self._menus = {};
    kernel_menu    = self._menus['MeqTimba'] = QPopupMenu(self);
    bookmarks_menu = self._menus['Bookmarks'] = QPopupMenu(self);
    view_menu      = self._menus['View'] = QPopupMenu(self);
    debug_menu     = self._menus['Debug'] = QPopupMenu(self);
    help_menu      = self._menus['Help'] = QPopupMenu(self);

    menubar = self.menuBar();    
    kernel_menu_id = menubar.insertItem("&MeqTimba",kernel_menu);
    window_menu_id = menubar.insertItem("&View",view_menu);
    bookmarks_menu_id = menubar.insertItem("&Bookmarks",bookmarks_menu);
    debug_menu_id = menubar.insertItem("&Debugger",debug_menu);
    menubar.insertSeparator();
    help_menu_id = menubar.insertItem("&Help",help_menu);
    
    # some menus only available when connected
    QObject.connect(self,PYSIGNAL("connected()"),self.xcurry(menubar.setItemVisible,_args=(bookmarks_menu_id,True)));
    QObject.connect(self,PYSIGNAL("connected()"),self.xcurry(menubar.setItemVisible,_args=(debug_menu_id,True)));
    QObject.connect(self,PYSIGNAL("disconnected()"),self.xcurry(menubar.setItemVisible,_args=(bookmarks_menu_id,False)));
    QObject.connect(self,PYSIGNAL("disconnected()"),self.xcurry(menubar.setItemVisible,_args=(debug_menu_id,False)));
    menubar.setItemVisible(bookmarks_menu_id,False);
    menubar.setItemVisible(debug_menu_id,False);

    # --- MeqTimba menu
    connect = QAction("Connect to kernel...",0,self);    
    connect.addTo(kernel_menu);
    QObject.connect(self,PYSIGNAL("connected()"),self.xcurry(connect.setEnabled,_args=(False,)));
    QObject.connect(self,PYSIGNAL("disconnected()"),self.xcurry(connect.setEnabled,_args=(True,)));
    self.treebrowser._qa_refresh.addTo(kernel_menu);
    self.treebrowser._qa_load.addTo(kernel_menu);
    self.treebrowser._qa_save.addTo(kernel_menu);
    
    # --- View menu
    showgw = QAction(pixmaps.view_split.iconset(),"&Gridded workspace",Qt.Key_F3,self);
    showgw.addTo(view_menu);
    showgw.setToggleAction(True);
    QObject.connect(self.gw.wtop(),PYSIGNAL("shown()"),showgw.setOn);
    QObject.connect(showgw,SIGNAL("toggled(bool)"),self.gw.show);
    # optional tab views
    self.resultlog.wtop()._show_qaction.addTo(view_menu);
    self.eventtab._show_qaction.addTo(view_menu);
    # process status view
    showps = QAction("&Process status",0,self);
    showps.addTo(view_menu);
    showps.setToggleAction(True);
    showps.setOn(False);
    QObject.connect(showps,SIGNAL("toggled(bool)"),self._wstat.setShown);
    QObject.connect(self._wstat,PYSIGNAL("shown()"),showps.setOn);
    
    # --- Bookmarks menu
    self._qa_addbkmark = addbkmark = QAction(pixmaps.bookmark_add.iconset(),"Add bookmark",Qt.ALT+Qt.Key_B,self);
    addbkmark.addTo(bookmarks_menu);
    self._qa_addpagemark = addpagemark = QAction(pixmaps.bookmark_toolbar.iconset(),"Add bookmark for page",Qt.ALT+Qt.CTRL+Qt.Key_B,self);
    addpagemark.addTo(bookmarks_menu);
    QObject.connect(addbkmark,SIGNAL("activated()"),self._add_bookmark);
    QObject.connect(addpagemark,SIGNAL("activated()"),self._add_pagemark);
    QObject.connect(self.gw.wtop(),PYSIGNAL("shown()"),self._gw_reset_bookmark_actions);
    QObject.connect(self.gw.wtop(),PYSIGNAL("shown()"),self._gw_reset_bookmark_actions);
    QObject.connect(self.gw.wtop(),PYSIGNAL("itemSelected()"),self._gw_reset_bookmark_actions);
    QObject.connect(self.gw.wtop(),PYSIGNAL("pageShown()"),self._gw_reset_bookmark_actions);
    addbkmark.setEnabled(False);
    addpagemark.setEnabled(False);
    # bookmark manager
    bookmarks_menu.insertSeparator();
    self._bookmarks = bookmarks.BookmarkFolder("main",self,menu=bookmarks_menu);
    # copy of current bookmark record
    self._bookmarks_rec = None;
    QObject.connect(self._bookmarks,PYSIGNAL("updated()"),self._save_bookmarks);
    
    # --- Debug menu
    self.treebrowser._qa_dbg_enable.addTo(debug_menu);
    self.treebrowser._qa_dbg_tools.addTo(debug_menu);
    debug_menu.insertSeparator();
    attach_gdb = QAction("Attach debugger to kernel",0,self);
    attach_gdb.addTo(debug_menu);
    attach_gdb.setEnabled(False); # for now
    
    # --- Help menu
    help_menu.insertItem(QWhatsThis.whatsThisButton(self).iconSet(),
                              "What's &This",self.whatsThis,Qt.SHIFT+Qt.Key_F1);
    
    # populate menus from plugins                          
    # scan all modules for define_mainmenu_actions methods, and call them all
    self._actions = {};
    funcs = sets.Set();
    for (name,mod) in sys.modules.iteritems():
      _dprint(4,'looking for mainmenu actions in',name);
      try: 
        if callable(mod.define_mainmenu_actions):
          _dprint(3,'mainmenu action found in',name,'adding to set');
          funcs.add(mod.define_mainmenu_actions);
      except AttributeError: pass;
    _dprint(1,len(funcs),'unique mainmenu action-definition methods found');
    for f in funcs:
      f(self._menus);
      
    # finally, add standard stuff to bottom of menus
    kernel_menu.insertSeparator();
    exit = QAction(pixmaps.grey_round_cross.iconset(),"Quit browser",Qt.ALT+Qt.Key_Q,self);
    exit.addTo(kernel_menu);
    QObject.connect(exit,SIGNAL("activated()"),self.close);
 
    # subscribe to updates of forest state
    meqds.subscribe_forest_state(self._update_forest_state);
    
  def _add_bookmark (self):
    item = Grid.Services.getHighlightedItem();
    if item is not None:
      if not meqgui.isBookmarkable(item.udi):
        caption = "Can't set bookmark";
        text = "Item <b>"+item.name+"<b> is transient and thus cannot be bookmarked";
        QMessage(self,caption,text,QMessageBox.Cancel);
      else:
        vname = getattr(item.viewer,'viewer_name',item.viewer.__name__);
        name = "%s [%s]" % (item.name,vname);
        self._bookmarks.add(name,item.udi,item.viewer);

  def _add_pagemark (self):
    pass;
      
  def _save_bookmarks (self):
    """saves current bookmarks to forest state""";
    self._bookmarks_rec = self._bookmarks.getList();
    meqds.set_forest_state("bookmarks",self._bookmarks_rec);
    
  def _gw_reset_bookmark_actions (self,dum=None):
    # figure out if Add bookmark is enabled
    enable_bkmark = False;
    if self._connected and self.gw.isVisible():
      item = Grid.Services.getHighlightedItem();
      if item:
        enable_bkmark = meqgui.isBookmarkable(item.udi);
        if enable_bkmark:
          self._qa_addbkmark.setMenuText("Add bookmark for "+item.name);
    self._qa_addbkmark.setEnabled(enable_bkmark);
    if not enable_bkmark:
      self._qa_addbkmark.setMenuText("Add bookmark");
    # figure out if Add bookmark for page is enabled
    # self._qa_addpagemark.setEnabled(self._connected and self.gw.isVisible());
    self._qa_addpagemark.setEnabled(False);
        
  def _connected_event (self,ev,value):  
    app_proxy_gui._connected_event(self,ev,value);
    self._wstat.show();
    self._wstat.emit(PYSIGNAL("shown()"),(True,));
    self.treebrowser.clear();
    self.treebrowser.connected(True);  
    self.resultlog.connected(True);
    self._gw_reset_bookmark_actions();
    wtop = self.resultlog.wtop();
    self.maintab.changeTab(wtop,wtop._default_iconset,wtop._default_label);
    meqds.request_forest_state();
      
  def _disconnected_event (self,ev,value):  
    app_proxy_gui._disconnected_event(self,ev,value);
    self._wstat.hide();
    self._wstat.emit(PYSIGNAL("shown()"),(False,));
    self.treebrowser.connected(False);  
    self.resultlog.connected(False);
    self._gw_reset_bookmark_actions();
    wtop = self.resultlog.wtop();
    self.maintab.changeTab(wtop,wtop._default_iconset,wtop._default_label);
    
  def ce_ProcessStatus (self,ev,value):
    _dprint(5,'status:',ev,value);
    self._wstat.setStatus(map(int,value));
    
  def _checkStateUpdate (self,ev,value):
    try: 
      state = value.node_state;
      name  = state.name;
    except AttributeError: 
      return None;
    _dprint(5,'got state for node ',name);
    self.update_node_state(state,ev);
    return True;
    
  _prefix_NodeStatus = hiid('node.status');
  # override handleAppEvent to catch node state updates, whichever event they
  # may be in
  def handleAppEvent (self,ev,value):
    # check for node status
    if ev.startswith(self._prefix_NodeStatus):
      (ni,status,rqid) = (ev.get(2),ev.get(3),ev[4:]);
      _dprint(5,'got status for node',ni,':',status,rqid);
      try: node = meqds.nodelist[ni];
      except KeyError: pass;
      else: node.update_status(status,rqid);
    if isinstance(value,record):
      # check if message includes update of node state
      self._checkStateUpdate(ev,value);
      # check if message includes update of forest status
      fstatus = getattr(value,'forest_status',None);
      fstate  = getattr(value,'forest_state',None);
      if fstatus is not None:
        self.treebrowser.update_forest_status(fstatus);
      # update forest state, if supplied. Merge in the forest status if
      # we also have it
      if fstate is not None:
        if fstatus is not None:
          fstate.update(fstatus);
        meqds.update_forest_state(fstate);
      # no forest state supplied but a status is: merge it in
      elif fstatus is not None:
        meqds.update_forest_state(fstatus,True);
    # call top-level handler
    app_proxy_gui.handleAppEvent(self,ev,value);
    
  def ce_NodeState (self,ev,value):
    if hasattr(value,'name'):
      _dprint(5,'got state for node ',value.name);
      self.update_node_state(value,ev);
      
  def ce_NodeResult (self,ev,value):
    self.update_node_state(value,ev);
    if self.resultlog.enabled:
      txt = '';
      name = getattr(value,'name','') or '<unnamed>';
      cls  = getattr(value,'class','') or '?';
      rqid = str(getattr(value,'request_id',None)) or None;
      txt = ''.join((name,' <',cls.lower(),'>'));
      desc = 'snapshot for %s (%s)' % (name,cls);
      caption = '<B>%s</B> s/shot' % (name,);
      if rqid:
        txt = ''.join((txt,' rqid:',rqid));
        desc = desc + '; rqid: ' + rqid;
        caption = caption + ( ' <small>(rqid: %s)</small>' % (rqid,) );
      udi = meqds.snapshot_udi(value);
      self.resultlog.add(txt,content=value,category=Logger.Event,
        udi=udi,name=name,desc=desc,caption=caption,viewopts=meqgui.defaultResultViewopts);
      wtop = self.resultlog.wtop();
      if self.maintab.currentPage() is not wtop and not wtop._newresults:
        self.maintab.changeTab(wtop,wtop._newres_iconset,wtop._newres_label);
        wtop._newresults = True;
        
  def ce_LoadNodeList (self,ev,meqnl):
    if not meqds.nodelist.is_valid_meqnodelist(meqnl):
      _dprint(2,"got nodelist but it is not valid, ignoring");
      return;
    meqds.nodelist.load(meqnl);
    _dprintf(2,"loaded %d nodes into nodelist\n",len(meqds.nodelist));
    self.treebrowser.update_nodelist();
    # re-update forest status, if available
    try: fst = meqnl.forest_status;
    except AttributeError: pass;
    else: self.treebrowser.update_forest_status(fst);
    
  def ce_UpdateAppStatus (self,ev,status):
    try: nt = status.num_tiles;
    except AttributeError: pass;
    else:
      if self.app.state == treebrowser.AppState.Stream:
        state = self.app.statestr.lower();
        self.status_label.setText(' %s (%d) ' % (state,nt) ); 
        
  def update_node_state (self,node,event=None):
    meqds.reclassify_nodestate(node);
    meqds.add_node_snapshot(node,event);
    udi = meqds.node_udi(node);
    Grid.updateDataItem(udi,node);
    
  def _view_node (self,node,viewer=None,kws={}):
    _dprint(2,"node clicked, adding item");
    node = meqds.nodeobject(node);
    Grid.addDataItem(makeNodeDataItem(node,viewer),**kws);
    self.show_gridded_workspace();
    
  def _view_forest_state (self,viewer=None,**kws):
    _dprint(2,"adding viewer for forest state");
    item = meqgui.makeForestDataItem(viewer=viewer);
    Grid.addDataItem(item,**kws);
    self.show_gridded_workspace();
    
  def _update_forest_state (self,fst):
    # update bookmarks if needed
    bkrec = getattr(fst,'bookmarks',None);
    if bkrec != self._bookmarks_rec:
      _dprint(1,"bookmarks changed in forest, reloading");
      self._bookmarks_rec = bkrec;
      self._bookmarks.load(bkrec);
    else:
      _dprint(3,"bookmarks not changed in forest, ignoring");
    Grid.updateDataItem('/forest',fst);
    
  def _reset_resultlog_label (self,tabwin):
    if tabwin is self.resultlog.wtop() and tabwin._newresults:
      self._reset_maintab_label(tabwin);
    tabwin._newresults = False;

  def _update_app_state (self):
    app_proxy_gui._update_app_state(self);
    if self.app.state == treebrowser.AppState.Stream:
      self.ce_UpdateAppStatus(None,self.app.status);
    self.treebrowser.update_app_state(self.app.state);

# register NodeBrowser at low priority for now (still experimental),
# but eventually we'll make it the default viewer
# Grid.Services.registerViewer(meqds.NodeClass(),NodeBrowser,priority=30);

# register reloadables
reloadableModule(__name__);
# reloadableModule('meqds');


define([
    'dojo/Evented',

    'dojo/_base/declare',
    
    'dojo/on',

    'dijit/_WidgetBase',
    'dijit/_WidgetsInTemplateMixin',
    'dijit/_TemplatedMixin',

    'dojo/text!./templates/widget.html'
], function(
    Evented,
    declare,
    on,
    _WidgetBase, _WidgetsInTemplateMixin, _TemplatedMixin,
    template
) {

    var selector = declare('Selector', [_WidgetBase, _TemplatedMixin, _WidgetsInTemplateMixin, Evented], {

        declaredClass: "esri.widgets.Selector",

        templateString: template,

        items: [],

        selectedIndex: 0,

        //--------------------------------------------------------------------------
        //
        //  Lifecycle
        //
        //--------------------------------------------------------------------------

        constructor: function(options) {
            this.items = options.items || [];
            this.selectedIndex = options.selectedIndex || 0;
        },

        postCreate: function() {
            this.inherited(arguments);
            if(this.items.length > 0) {
                this._popItems();
            }
            this.selNode.addEventListener("click", this._click.bind(this));
        },

        startup: function() {
            //this.inherited(arguments);
        },

        select: function(index) {
            var nodes = this.itemsNode.getElementsByClassName("item");
            nodes[this.selectedIndex].classList.remove("chk");
            this.selectedIndex = index;
            nodes[this.selectedIndex].classList.add("chk");
            var item = this.items[this.selectedIndex];
            this.selNode.innerHTML = item.label;
        },

        _click: function() {
            this.itemsNode.classList.toggle("collapsed");
        },

        _popItems: function() {
            var node = this.itemsNode;
            node.innerHTML = "";
            this.items.forEach(function(i, idx) {
                var item = document.createElement("div");
                item.classList.add("item");
                if(idx === this.selectedIndex) {
                    this.selNode.innerHTML = i.label;
                    item.classList.add("chk");
                }
                item.setAttribute("title", i.label);
                item.innerHTML = i.label;
                on(item, "click", this._clickItem.bind(this));                
                node.appendChild(item);
            }, this);
        },

        _clickItem: function(evt) {
            var nodes = this.itemsNode.getElementsByClassName("item");
            nodes[this.selectedIndex].classList.remove("chk");
            var t = evt.target;
            for(var i = 0; i < nodes.length; i++) {
                if(nodes[i] === t) {
                    this.selectedIndex = i;
                    this._select();
                    break;
                }
            }
        },

        _select: function() {
            var item = this.items[this.selectedIndex];
            this.selNode.innerHTML = item.label;
            this.itemsNode.classList.add("collapsed");
            var nodes = this.itemsNode.getElementsByClassName("item");
            nodes[this.selectedIndex].classList.add("chk");
            var data = {
                selectedIndex: this.selectedIndex,
                item: item
            };
            this.emit("change", data);
        }

    });

    return selector;
});
/*
 * File: app/view/ui/serviceEditor.js
 * Date: Thu May 22 2014 15:17:28 GMT+0200 (CEST)
 *
 * This file was generated by Ext Designer version 1.2.3.
 * http://www.sencha.com/products/designer/
 *
 * This file will be auto-generated each and everytime you export.
 *
 * Do NOT hand edit this file.
 */

Ext.define('istsos.view.ui.serviceEditor', {
    extend: 'Ext.panel.Panel',

    border: 0,
    title: '',

    initComponent: function() {
        var me = this;

        Ext.applyIf(me, {
            items: [
                {
                    xtype: 'form',
                    border: 0,
                    id: 'frmServices',
                    bodyPadding: 10,
                    title: '',
                    trackResetOnLoad: true,
                    items: [
                        {
                            xtype: 'fieldset',
                            title: 'Quality index',
                            items: [
                                {
                                    xtype: 'textfield',
                                    id: 'opService',
                                    name: 'service',
                                    fieldLabel: 'Name',
                                    anchor: '100%'
                                }
                            ]
                        }
                    ],
                    dockedItems: [
                        {
                            xtype: 'toolbar',
                            ui: 'footer',
                            dock: 'bottom',
                            layout: {
                                pack: 'center',
                                type: 'hbox'
                            },
                            items: [
                                {
                                    xtype: 'button',
                                    id: 'btnForm',
                                    text: 'New'
                                }
                            ]
                        }
                    ]
                },
                {
                    xtype: 'gridpanel',
                    id: 'gridop',
                    margin: 8,
                    title: '',
                    forceFit: true,
                    store: 'storeServices',
                    viewConfig: {

                    },
                    dockedItems: [
                        {
                            xtype: 'toolbar',
                            dock: 'top',
                            items: [
                                {
                                    xtype: 'button',
                                    id: 'btnNew',
                                    text: 'New'
                                },
                                {
                                    xtype: 'button',
                                    disabled: true,
                                    id: 'btnRemove',
                                    text: 'Remove'
                                }
                            ]
                        }
                    ],
                    columns: [
                        {
                            xtype: 'gridcolumn',
                            dataIndex: 'service',
                            text: 'Service'
                        },
                        {
                            xtype: 'gridcolumn',
                            dataIndex: 'path',
                            text: 'Path'
                        }
                    ]
                }
            ]
        });

        me.callParent(arguments);
    }
});
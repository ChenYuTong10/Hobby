// components/downlist/downlist.js
Component({
    /**
     * 组件的属性列表
     */
    properties: {
        headers:{
            type:Array,
            value:[]
        },
        courses:{
            type:Object,
            value:{}
        }
    },

    /**
     * 组件的初始数据
     */
    data: {

    },

    /**
     * 组件的方法列表
     */
    methods: {
        handleDownListTapped(){
            this.triggerEvent("DownListTapped");
        }
    }
})

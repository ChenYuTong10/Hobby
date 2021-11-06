// components/tabs/tabs.js
Component({
    /**
     * 组件的属性列表
     */
    properties: {
        tabs:{
            type:Array,
            value:[]
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
        handleTabsTap(e){
            const tapped_index = e.target.dataset.index;    /*"target"和"currentTarget"的区别注意一下啊*/
            this.triggerEvent("TabsTappedChange",{tapped_index});
        }
    }
})

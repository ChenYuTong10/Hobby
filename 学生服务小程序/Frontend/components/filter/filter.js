// components/filter/filter.js
Component({
    /**
     * 组件的属性列表
     */
    properties: {
        filter:{
            type:Array,
            value:[]
        }
    },

    /**
     * 组件的初始数据
     */
    data: {
        isActive:false
    },

    /**
     * 组件的方法列表
     */
    methods: {
        //开关筛选器
        handleFilterTapped(){
            let isActive = this.data.isActive;
            this.setData({
                isActive:!isActive
            });
        },
        //点击选项
        handleFilterItemTapped(e){
            const father_index = e.currentTarget.dataset.father_index;
            const children_index = e.currentTarget.dataset.children_index;
            this.triggerEvent("FilterTappedChange", {father_index,children_index});
        },
        //重置按钮
        handleReset(){
            this.triggerEvent("FilterReset");
        },
        //确定按钮
        handleConfirm(e){
            //关闭筛选器
            this.setData({
                isActive:false
            });
            this.triggerEvent("FilterConfirm");
        }
    }
})

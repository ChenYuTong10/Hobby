import {request} from "../../request/request.js"
import {showLoading,showModal,showToast} from "../../utils/util.js"

Page({
    data: {
        tabs:[
            {
                id:0,
                name:"待维修",
                isActive:true
            },
            {
                id:1,
                name:"已维修",
                isActive:false
            }
        ],
        username:"",
        repairing_list:[],
        repaired_list:[]
    },
    //请求参数
    params:{
        url:'',
        method:'',
        data:{},
        timeout:3000
    },
    async getRepairingList(){
        showLoading({"title":"加载中..."});
        //获取用户名
        const username = this.data.username;
        //配置请求参数
        this.params.url = "https://u4363536m9.zicp.vip/retrieve/repair/waiting?username=" + username;
        this.params.method = 'GET';
        this.params.data = {};
        //请求数据
        const result = await request(this.params);
        //检查返回结果
        if(result===undefined){
            showToast({"title":"请求超时","icon":"error"});
        }
        else{
            this.setData({
                repairing_list:result.data.details
            });
        }
        wx.hideLoading();
    },
    async getRepairedList(){
        showLoading({"title":"加载中..."});
        //获取用户名
        const username = this.data.username;
        //配置请求参数
        this.params.url = "https://u4363536m9.zicp.vip/retrieve/repair/finished?username=" + username;
        this.params.method = 'GET';
        this.params.data = {};
        //请求数据
        const result = await request(this.params);
        //检查返回结果
        if(result===undefined){
            showToast({"title":"请求超时","icon":"error"});
        }
        else{
            this.setData({
                repaired_list:result.data.details
            });
        }
        wx.hideLoading();
    },
    //标题栏点击事件
    handleTabsTappedChange(e){
        const tapped_index = e.detail.tapped_index;
        let tabs = JSON.parse(JSON.stringify(this.data.tabs));
        tabs.forEach((v,i)=>{i==tapped_index?v.isActive=true:v.isActive=false});
        this.setData({
            tabs:tabs
        });
    },
    //修改报修信息
    async handleRepairInfoModification(e){
        const result = await showModal({"title":"提示","content":"确定需要修改吗"});
        if(result.confirm){
            const modify_item_id = e.currentTarget.dataset.id;
            wx.navigateTo({
                url: '/pages/repair/index?modify_item_id=' + modify_item_id
            });
        }
    },
    //取消报修
    async handleRepairInfoBackout(e){
        const result = await showModal({"title":"提示","content":"确定要取消吗"});
        if(result.confirm){
            //获取id
            const delete_item_id = e.currentTarget.dataset.id;
            //配置请求参数
            this.params.url = "https://u4363536m9.zicp.vip/delete/repair?id=" + delete_item_id;
            this.params.method = 'DELETE';
            this.params.data= {};
            //请求删除
            const result = await request(this.params);
            //返回结果检验
            if(result === undefined){
                showToast({"title":"请求超时", "icon":"error"});
                return;
            }
            if(result.data.status!==200){
                showToast({"title":"请稍后重试","icon":"error"});
                return;
            }
            //刷新数据
            let repairing_list = JSON.parse(JSON.stringify(this.data.repairing_list));
            repairing_list.splice(repairing_list[delete_item_id],1);
            this.setData({
                repairing_list:repairing_list
            });
            wx.setStorageSync("repairing_list", repairing_list);
            showToast({"title":"删除成功", "icon":"success"});
        }
    },
    onShow: function () {
        //获取用户名
        let pages = getCurrentPages();
        let current_page = pages[pages.length-1];
        const username = current_page.options.username;
        if(username===undefined){
            showToast({"title":"您还没有登录","icon":"error"});
            return;
        }
        this.setData({
            username:username
        });
        //获取数据
        this.getRepairingList();
        this.getRepairedList();
    },
    onPullDownRefresh: function () {
        showLoading({"title":"刷新中"});
        //获取数据
        this.getRepairingList();
        this.getRepairedList();
        //后续操作
        wx.hideLoading();
        wx.stopPullDownRefresh();
    }
})
import {request} from "../../request/request.js"
import {showLoading, showToast} from "../../utils/util.js"

Page({
    data: {
        username:"",
        repair_info:{}
    },
    //请求参数
    params:{
        url:'',
        method:'',
        data:{},
        timeout:3000
    },
    //输入事件
    handleInputName(e){
        this.setData({
            "repair_info.name":e.detail.value
        });
    },
    handleInputPhone(e){
        this.setData({
            "repair_info.phone":e.detail.value
        });
    },
    handleInputDorm(e){
        this.setData({
            "repair_info.dorm":e.detail.value
        });
    },
    handleInputDetails(e){
        this.setData({
            "repair_info.details":e.detail.value
        });
    },
    /*正则表达式*/
    phone_pattern:/^[\d]+$/,
    //对表单进行检查
    async handleSubmit(){
        const username = this.data.username;
        const repair_info = this.data.repair_info;
        //数据检查
        if(!username){
            wx.navigateTo({
                url: '/pages/login/index'
            });
            return;
        }
        if(!repair_info.name.trim()){
            showToast({"title":"姓名不能为空","icon":"none"});
            return; 
        }
        if(!this.phone_pattern.test(repair_info.phone)||repair_info.phone.length!=11){
            showToast({"title":"手机号为空或格式不正确","icon":"none"});
            return;
        }
        if(!repair_info.dorm.trim()){
            showToast({"title":"宿舍不能为空","icon":"none"});
            return;
        }
        if(!repair_info.details.trim()){
            showToast({"title":"故障情况不能为空","icon":"none"})
            return;
        }
        //配置请求参数
        this.params.url = "https://u4363536m9.zicp.vip/create/repair";
        this.params.method = "POST";
        this.params.data = {
            "username": username,
            "repair_info":repair_info
        };
        //上传数据
        showLoading({"title":"正在提交"});
        const result = await request(this.params);
        //返回结果检查
        if(result === undefined){
            showToast({"title":"请求超时","icon":"error"});
            return;
        }
        if(result.data.status !== 200){
            showToast({"title":"提交失败","icon":"error"});
            return;
        }
        //后续处理操作
        wx.navigateBack({
            delta: 1
        });
        showToast({"title":"提交成功","icon":"success"});
    },
    onShow: function () {
        //获取个人昵称
        const userInfo = wx.getStorageSync("userInfo")||{};
        this.setData({
            username:(userInfo.nickName===undefined?"":userInfo.nickName)
        });
        //获取修改项id
        let pages = getCurrentPages();
        let current_page = pages[pages.length-1];
        const modify_item_id = current_page.options.modify_item_id;
        if(modify_item_id===undefined){return;}
        //从缓存中取出
        const repairing_list = wx.getStorageSync("repairing_list") || [];
        const repair_info = repairing_list.data.find((v)=>(v.id == modify_item_id));
        this.setData({
            repair_info:repair_info
        });
    }
})
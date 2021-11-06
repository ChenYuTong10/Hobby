// pages/setting/index.js
import {chooseImage,showLoading,showToast,showModal,uploadFile} from "../../utils/util.js"

Page({

    /**
     * 页面的初始数据
     */
    data: {
        userInfo:{},
        feedback_content:"",
        upimageList:[],
        feedback_type:"错误反馈",
        typeList:[
            {
                id:0,
                name:"错误反馈",
                value:"错误反馈",
                isChecked:true
            },
            {

                id:1,
                name:"功能建议",
                value:"功能建议",
                isChecked:false
            },
            {
                id:2,
                name:"其他方面",
                value:"其他方面",
                isChecked:false
            }
        ]
    },
    params:{
        url:'',
        method:'',
        data:''
    },
    //监听输入
    handleFeedbackInput(e){
        const value = e.detail.value;
        this.setData({
            feedback_content:value
        });
    },
    //监听单选按钮变化
    handleRadioChange(e){
        this.setData({
            feedback_type:e.detail.value
        });
    },
    //上传反馈图片
    async handleUpLoadImage(){
        const result = await chooseImage();
        //判断用户是否选择图片
        if(result!==undefined){
            this.setData({
                upimageList:[...this.data.upimageList,...result.tempFilePaths]
            });
            showToast({"title":"上传成功","icon":"success"});
        }
    },
    //放大反馈图片
    handlePreviewImage(e){
        const upimageList = JSON.parse(JSON.stringify(this.data.upimageList));
        const tapped_image_index = e.currentTarget.dataset.index;
        wx.previewImage({
            current: upimageList[tapped_image_index],
            urls: upimageList
        });
    },
    //删除反馈图片
    handleDeleteImage(e){
        const upimageList = JSON.parse(JSON.stringify(this.data.upimageList));
        const tapped_image_index = e.currentTarget.dataset.index;
        upimageList.splice(tapped_image_index,1);
        this.setData({
            upimageList:upimageList
        });
    },
    //表单提交
    async handleSubmit(){
        //检查数据
        const userInfo = this.data.userInfo;
        const feedback_content = this.data.feedback_content;
        const upimageList = this.data.upimageList;
        const feedback_type = this.data.feedback_type;
        //检查登录
        if(!userInfo.nickName){
            const result = await showModal({"title":"提示","content":"您还没有登录"});
            if(result.confirm){
                wx.navigateTo({
                    url: '/pages/login/index'
                });
            }
            return;
        }
        if(!feedback_content.trim()){
            showModal({"title":"提示","content":"反馈意见不能为空"});
            return;
        }
        const formData = {"poster":userInfo.nickName,"content":feedback_content,"type":feedback_type}
        //上传数据
        showLoading({"title":"正在上传中"});
        for (let index = 0; index < upimageList.length; index++) {
            let result = await uploadFile({"filePath":upimageList[index],"formData":formData});
            //这里是因为上传数据的返回值为"string",坑人!!!!!
            if(result === undefined || JSON.parse(result.data).status !== 200){
                showToast({"title":"请求超时","icon":"error"});
                return;
            }
        }
        wx.navigateBack({
            delta: 1
        });
        showToast({"title":"反馈成功","icon":"success"});
    },

    /**
     * 生命周期函数--监听页面加载
     */
    onLoad: function (options) {

    },

    /**
     * 生命周期函数--监听页面初次渲染完成
     */
    onReady: function () {

    },

    /**
     * 生命周期函数--监听页面显示
     */
    onShow: function () {
        this.data.userInfo = wx.getStorageSync("userInfo")||{};
    },

    /**
     * 生命周期函数--监听页面隐藏
     */
    onHide: function () {

    },

    /**
     * 生命周期函数--监听页面卸载
     */
    onUnload: function () {

    },

    /**
     * 页面相关事件处理函数--监听用户下拉动作
     */
    onPullDownRefresh: function () {

    },

    /**
     * 页面上拉触底事件的处理函数
     */
    onReachBottom: function () {

    },

    /**
     * 用户点击右上角分享
     */
    onShareAppMessage: function () {

    }
})
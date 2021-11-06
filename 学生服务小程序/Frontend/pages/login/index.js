// pages/login/index.js
import {showLoading,showToast,getUserProfile} from "../../utils/util.js"

Page({

    /**
     * 页面的初始数据
     */
    data: {

    },
    async handleLogin(){
        showLoading({"title":"正在登录中"});
        const result = await getUserProfile({"desc":"用于个人登录"});
        //判断用户是否允许
        if(result !== undefined){
            const userInfo = result.userInfo;
            wx.setStorageSync("userInfo", userInfo);
            wx.navigateBack({
                delta: 1
            });
            showToast({"title":"登陆成功","icon":"success"});
        }
        else{
            wx.hideLoading();
        }
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
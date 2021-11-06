// pages/timetable/index.js
import {request} from "../../request/request.js"

Page({

    /**
     * 页面的初始数据
     */
    data: {
        weekList:["周一","周二","周三","周四","周五","周六","周七"],
        hourList:[
            {
                id:0,
                time:"8:00-9:00"
            },
            {
                id:1,
                time:"9:00-10:00"
            },
            {
                id:2,
                time:"10:00-11:00"
            },
            {
                id:3,
                time:"11:00-12:00"
            },
            {
                id:4,
                time:"12:00-13:00"
            },
            {
                id:5,
                time:"13:00-14:00"
            },
            {
                id:6,
                time:"14:00-15:00"
            },
            {
                id:7,
                time:"15:00-16:00"
            },
            {
                id:8,
                time:"16:00-17:00"
            },
            {
                id:9,
                time:"17:00-18:00"
            },
            {
                id:10,
                time:"18:00-19:00"
            },
            {
                id:11,
                time:"19:00-20:00"
            },
            {
                id:12,
                time:"20:00-21:00"
            }
        ],
        courseList:[]
    },
    getCourseList(){
        let courseList = wx.getStorageSync("courses")||[];
        if(courseList.length){
            courseList.forEach(v=>{
                v["start_time"] = this.formatTime(v["start_time"]);
                v["end_time"] = this.formatTime(v["end_time"]);
            });
        }
        this.setData({
            courseList:courseList
        });
    },
    handleNavigateCourseManagement(e){
        wx.navigateTo({
            url: '/pages/course_management/index'
        });
    },
    handleNavigateCourseDetails(e){
        wx.navigateTo({
            url: '/pages/course_detail/index?index='+e.currentTarget.dataset.index
        });
    },
    //格式化时间:以小时做单位
    formatTime(time){
        let hour = Number(time[0]+time[1]);
        let minute = Number(time[3]+time[4]) / 60;
        return (hour + minute);
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
        this.getCourseList();
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
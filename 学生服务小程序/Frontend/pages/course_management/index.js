// pages/course/index.js
import {request} from "../../request/request.js"
import {showToast,showLoading,showModal} from "../../utils/util.js"

Page({

    /**
     * 页面的初始数据
     */
    data: {
        tabs:[
            {
                id:0,
                name:"添加课程",
                isActive:true
            },
            {
                id:1,
                name:"导入课表",
                isActive:false
            }
        ],
        weekList:[[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20],[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]],
        dayList:[
            {
                id:1,
                name:"周一",
                day:"Monday"
            },
            {
                id:2,
                name:"周二",
                day:"Tuesday"
            },
            {
                id:3,
                name:"周三",
                day:"Wednesday"
            },
            {
                id:4,
                name:"周四",
                day:"Thursday"
            },
            {
                id:5,
                name:"周五",
                day:"Friday"
            },
            {
                id:6,
                name:"周六",
                day:"Saturday"
            },
            {
                id:7,
                name:"周七",
                day:"Sunday"
            }
        ],
        userInfo:{},
        //课程信息
        course_name:"",
        course_room:"",
        weekList_index:[0,19],
        dayList_index:0,
        start_time:"08:30",
        end_time:"20:45",
        lecturer:"",
        remark:"",
        //登录信息
        username:"",
        password:""
    },
    //登录信息
    params:{
        url:'',
        method:'',
        data:{}
    },
    //全部课程信息
    courses:[],
    //标签栏
    handleTabsTappedChange(e){
        const tapped_index = e.detail.tapped_index;
        let tabs = JSON.parse(JSON.stringify(this.data.tabs));
        tabs.forEach((v,i)=>{i==tapped_index?v.isActive=true:v.isActive=false});
        this.setData({
            tabs:tabs
        });
    },

    //添加课程页面参数
    //输入事件
    handleInputCourseName(e){
        this.setData({
            course_name:e.detail.value
        });
    },
    handleInputCourseRoom(e){
        this.setData({
            course_room:e.detail.value
        });
    },
    handleInputLecturer(e){
        this.setData({
            lecturer:e.detail.value
        });
    },
    handleInputRemark(e){
        this.setData({
            remark:e.detail.value
        });
    },
    handleUsernameInput(e){
        this.setData({
            username:e.detail.value
        });
    },
    handlePasswordInput(e){
        this.setData({
            password:e.detail.value
        });
    },
    //改变滚轮选择器选中的item
    handleWeekChange(e){
        const weekList_index = e.detail.value;
        this.setData({
            weekList_index:weekList_index
        });
    },
    handleDayChange(e){
        const dayList_index = e.detail.value;
        this.setData({
            dayList_index:dayList_index,
        });
    },
    handleStartTimeChange(e){
        const start_time = e.detail.value;
        this.setData({
            start_time:start_time
        });
    },
    handleEndTimeChange(e){
        const end_time = e.detail.value;
        this.setData({
            end_time:end_time,
        });
    },
    //检查时间
    handleCheckTime(start_time,end_time){
        //先对小时进行比较
        let start_time_hour = Number(start_time[0]+start_time[1]);
        let end_time_hour = Number(end_time[0]+end_time[1]);
        if(end_time_hour-start_time_hour>0){return true;}
        if(end_time_hour-start_time_hour<0){return false;}
        //对分钟进行比较
        let start_time_minute = Number(start_time[3]+start_time[4]);
        let end_time_minute = Number(end_time[3]+end_time[4]);
        if(end_time_minute-start_time_minute<0){return false;}
        else{return true;}
    },
    //提交按钮
    async handleSubmit(){
        //【想法?】如果前面的数据如果不合法,那就没必要一下子把所有数据都获取,虽然我不知道这影响大不大
        //检查数据合法
        const course_name = this.data.course_name;
        const course_room = this.data.course_room;
        const dayList_index = this.data.dayList_index;
        let start_time = this.data.start_time;  //傻了吧,就知道用"const"
        let end_time = this.data.end_time;
        const weekList_index = this.data.weekList_index;
        const lecturer = this.data.lecturer;
        const remark = this.data.remark;
        if(!course_name.trim()){
            showToast({"title":"课程名称不能为空","icon":"none"});
            return;
        }
        if(!course_room.trim()){
            showToast({"title":"授课地点不能为空","icon":"none"});
            return;
        }
        if(start_time=="开始时间"){
            showToast({"title":"请选择课程开始时间","icon":"none"});
            return;
        }
        if(end_time=="结束时间"){
            showToast({"title":"请选择课程结束时间","icon":"none"});
            return;
        }
        //检查周数大小
        if(weekList_index[0]>weekList_index[1]){
            showToast({"title":"请选择正确的授课周数","icon":"none"});
            return;
        }
        //检查时间大小
        if(!this.handleCheckTime(start_time,end_time)){
            showToast({"title":"请选择正确的授课时间","icon":"none"});
            return;
        }
        if(!lecturer.trim()){
            showToast({"title":"授课教师不能为空","icon":"none"});
            return;
        }
        //数据合法则处理打包加入缓存
        const course = {"name":course_name,"classroom":course_room,
                        "day":this.data.dayList[dayList_index].value,
                        "start_time":start_time,"end_time":end_time,
                        "duration": this.data.weekList[0][weekList_index[0]]+"-"+this.data.weekList[1][weekList_index[1]]+"周",
                        "lecturer":lecturer,"remark":remark};
        this.courses.push(course);
        wx.setStorageSync("courses", this.courses);
        //回退到课程表
        wx.navigateBack({
            delta: 1
        });
        showToast({"title":"添加成功","icon":"success"});
    },
    //登录按钮
    async handleLogin(){
        const userInfo = this.data.userInfo;
        const username = this.data.username;
        const password = this.data.password;
        //检查数据合法
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
        if(!username.trim()){
            showToast({"title":"学号不能为空","icon":"none"});
            return;
        }
        if(!password.trim()){
            showToast({"title":"密码不能为空","icon":"none"});
            return;
        }
        //配置请求参数
        this.params.url = 'https://u4363536m9.zicp.vip/get/timetable';
        this.params.method = 'POST';
        this.params.data = {"username":username, "password":password};
        //发送请求
        showLoading({"title":"正在获取课程表"});
        const result = await request(this.params);
        if(result === undefined || result.data.status !== 200){
            showToast({"title":"登录失败","icon":"error"});
            return;
        }
        this.courses = result.data.details;
        wx.setStorageSync("courses", this.courses);
        //回退
        wx.navigateBack({
            delta: 1
        });
        showToast({"title":"登录成功","icon":"success"});
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
        //个人信息
        this.data.userInfo = wx.getStorageSync("userInfo")||{};
        //获得课程信息
        this.courses = wx.getStorageSync("courses")||[];
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
        //下拉重置
        this.setData({
            course_name:"",
            course_room:"",
            weekList_index:[0,19],
            dayList_index:0,
            start_time:"08:30",
            end_time:"20:45",
            lecturer:"",
            remark:"",
            username:"",
            password:""
        });
        wx.stopPullDownRefresh();
        showToast({"title":"刷新成功","icon":"success"});
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
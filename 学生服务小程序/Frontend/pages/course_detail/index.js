// pages/course/index.js
import {showToast,showModal} from "../../utils/util.js"

Page({

    /**
     * 页面的初始数据
     */
    data: {
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
        //课程信息
        course_name:"",
        course_room:"",
        weekList_index:[0,19],
        dayList_index:0,
        start_time:"",
        end_time:"",
        lecturer:"",
        remark:"",
        course_index:-1,
    },
    courses:[],

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
            dayList_index:dayList_index
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
            end_time:end_time
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
    handleStorage(){
        //检查数据合法
        const course_name = this.data.course_name;
        const course_room = this.data.course_room;
        const dayList_index = this.data.dayList_index;
        let start_time = this.data.start_time;  //傻了吧,就知道用"const"
        let end_time = this.data.end_time;
        const lecturer = this.data.lecturer;
        const remark = this.data.remark;
        const index = this.data.index;
        if(!course_name.trim()){
            showToast({"title":"课程名称不能为空","icon":"none"});
            return;
        }
        if(!course_room.trim()){
            showToast({"title":"授课地点不能为空","icon":"none"});
            return;
        }
        if(dayList_index==0){
            showToast({"title":"请选择周授课日","icon":"none"});
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
        const course = {"course_name":course_name,"course_room":course_room,"day":this.data.dayList[dayList_index].day,"start_time":start_time,"end_time":end_time,"lecturer":lecturer,"remark":remark};
        this.courses[course_index] = course;
        wx.setStorageSync("courses", this.courses);

        //回退到课程表
        wx.navigateBack({
            delta: 1
        });
        showToast({"title":"保存成功","icon":"success"});
    },
    //删除按钮
    async handleDelete(){
        const result = await showModal({"title":"提示","content":"确定要删除课程吗"});
        if(result.confirm){
            this.courses.splice(this.data.course_index,1);
            wx.setStorageSync("courses", this.courses);
            //回退
            wx.navigateBack({
                delta: 1
            });
            showToast({"title":"删除成功","icon":"success"});
        }
    },
    //将字符串周数转化为对应的数字
    handleTranslateWeekListIndex(duration){
        let location = 0; //便于记录周数下标的开始
        let first_index = 0;
        let second_index = 0;
        if(duration.charCodeAt(location+1)>=48 && duration.charCodeAt(location+1)<=57){
            first_index = Number(duration[location]+duration[location+1]);
            location = 3;
        }
        else{
            first_index = Number(duration[location]);
            location = 2;
        }
        if(duration.charCodeAt(location+1)>=48 && duration.charCodeAt(location+1)<=57){
            second_index = Number(duration[location]+duration[location+1]);
        }
        else{
            second_index = Number(duration[location]);
        }
        return [first_index,second_index];
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
        //获取页面参数
        let pages = getCurrentPages();
        let currentPage =  pages[pages.length-1];
        const course_index = currentPage.options.index;
        //获取课程数据
        this.courses = wx.getStorageSync("courses");
        const currentCourse = this.courses[course_index];
        //转化
        let translate_day = {"Monday":0,"Tuesday":1,"Wednesday":2,"Thursday":3,"Friday":4,"Saturaday":5,"Sunday":6};
        let weekList_index = this.handleTranslateWeekListIndex(currentCourse["duration"]);
        //赋值
        this.setData({
            //课程信息
            course_name:currentCourse["name"],
            course_room:currentCourse["classroom"],
            weekList_index:[weekList_index[0]-1,weekList_index[1]-1], //数组下标和真实的序号差1
            dayList_index:translate_day[currentCourse["day"]],
            start_time:currentCourse["start_time"],
            end_time:currentCourse["end_time"],
            lecturer:currentCourse["lecturer"],
            remark:currentCourse["remark"],
            course_index:course_index
        });
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
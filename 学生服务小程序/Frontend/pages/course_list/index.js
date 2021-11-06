import {request} from "../../request/request.js"
import {showLoading,showToast} from "../../utils/util.js"

Page({

    /**
     * 页面的初始数据
     */
    data: {
        tabs:[
            {
                id:0,
                name:"体育课程",
                isActive:true
            },
            {
                id:1,
                name:"选修课程",
                isActive:false
            }
        ],
        sports_courses_filter:[
            {
                id:0,
                title:"活动场地",
                content:[
                    {
                        name:"教学楼",
                        isActive:false
                    },
                    {
                        name:"北区运动场",
                        isActive:false
                    },
                    {
                        name:"东区运动场",
                        isActive:false,
                    }
                ]
            },
            {
                id:1,
                title:"运动类型",
                content:[
                    {
                        name:"足球",
                        isActive:false
                    },
                    {
                        name:"篮球",
                        isActive:false
                    },
                    {
                        name:"毽球",
                        isActive:false
                    },
                    {
                        name:"乒乓球",
                        isActive:false
                    },
                    {
                        name:"排球",
                        isActive:false
                    },
                    {
                        name:"网球",
                        isActive:false
                    },
                    {
                        name:"轮滑",
                        isActive:false
                    },
                    {
                        name:"武术",
                        isActive:false,
                    },
                    {
                        name:"散打",
                        isActive:false
                    },
                    {
                        name:"跆拳道",
                        isActive:false
                    },
                    {
                        name:"体育舞蹈",
                        isActive:false
                    }
                ]
            }
        ],
        general_courses_filter:[
                {
                    id:0,
                    title:"学分",
                    content:[
                        {
                            name:0.5,
                            isActive:false
                        },
                        {
                            name:1.0,
                            isActive:false
                        },
                        {
                            name:1.5,
                            isActive:false
                        },
                        {
                            name:2.0,
                            isActive:false
                        },
                    ]
                },
                {
                    id:1,
                    title:"周授课日",
                    content:[
                        {
                            name:"星期一",
                            isActive:false
                        },
                        {
                            name:"星期二",
                            isActive:false
                        },
                        {
                            name:"星期三",
                            isActive:false
                        },
                        {
                            name:"星期四",
                            isActive:false
                        },
                        {
                            name:"星期五",
                            isActive:false
                        },
                        {
                            name:"星期六",
                            isActive:false
                        },
                        {
                            name:"星期七",
                            isActive:false
                        },
                    ]
                },
                {
                    id:2,
                    title:"授课类型",
                    content:[
                        {
                            name:"历史与文化",
                            isActive:false
                        },
                        {
                            name:"科学与技术",
                            isActive:false
                        },
                        {
                            name:"社会与经济",
                            isActive:false
                        },
                        {
                            name:"哲学与逻辑",
                            isActive:false
                        },
                        {
                            name:"创新与创业",
                            isActive:false   
                        },
                        {
                            name:"运动与健康",
                            isActive:false
                        },
                        {
                            name:"艺术与审美",
                            isActive:false
                        }
                    ]
                }
        ],
        sports_courses_headers:["授课教师","联系方式","授课时间","授课地点"],
        general_courses_headers:["授课教师","授课时间","授课地点", "授课模式", "备注"],
        sports_courses:[],
        general_courses:[],
    },
    //请求参数
    params:{
        url:'',
        method:'',
        data:{},
        timeout:3000
    },
    //页数参数
    sports_courses_page:{"total_pages":0,"page_number":1},
    general_courses_page:{"total_pages":0,"page_number":1},
    //标签栏
    handleTabsTappedChange(e){
        const tapped_index = e.detail.tapped_index;
        let tabs = JSON.parse(JSON.stringify(this.data.tabs));
        tabs.forEach((v,i)=>{i==tapped_index?v.isActive=true:v.isActive=false});
        this.setData({
            tabs:tabs
        });
    },
    //筛选器点击选项
    handleFilterTappedChange(father_index, children_index, filter){
        //限制单选
        filter[father_index].content.forEach((v,i)=>{
            i==children_index?v.isActive=!v.isActive:v.isActive=false
        });
        return filter;
    },
    handleSportsCoursesFilterChange(e){
        const father_index = e.detail.father_index;
        const children_index = e.detail.children_index;
        //限制单选
        let sports_courses_filter = this.handleFilterTappedChange(father_index, children_index, this.data.sports_courses_filter);
        //传回去
        this.setData({
            sports_courses_filter:sports_courses_filter
        });
    },
    handleGeneralCoursesFilterChange(e){
        const father_index = e.detail.father_index;
        const children_index = e.detail.children_index;
        //限制单选
        let general_courses_filter = this.handleFilterTappedChange(father_index, children_index, this.data.general_courses_filter);
        //传回去
        this.setData({
            general_courses_filter:general_courses_filter
        });
    },
    //重置筛选器
    handelFilterReset(filter){
        filter.forEach(father_v=>{
            father_v.content.forEach(children_v=>{
                children_v.isActive = false;
            });
        });
        return filter;
    },
    handleSportsCoursesFilterReset(){
        let sports_courses_filter = this.handelFilterReset(this.data.sports_courses_filter);
        this.setData({
            sports_courses_filter:sports_courses_filter
        });
    },
    handleGeneralCoursesFilterReset(){
        let general_courses_filter = this.handelFilterReset(this.data.general_courses_filter);
        this.setData({
            general_courses_filter:general_courses_filter
        });
    },
    //确定筛选器
    handleSportsCoursesFilterConfirm(){
        //将页码变成1
        this.sports_courses_page.page_number = 1;
        //清空原数据
        this.setData({
            sports_courses:[]
        });
        this.getSportsCoursesList();
    },
    handleGeneralCoursesFilterConfirm(){
        //将页码变成1
        this.general_courses_page.page_number = 1;
        //清空原数据
        this.setData({
            general_courses:[]
        });
        this.getGeneralCoursesList();
    },
    //点击下拉课程
    handleDownListTapped(index, courses){
        //改变激活状态
        courses[index].isActive = !courses[index].isActive;
        return courses;
    },
    handleSportsCoursesDownListTapped(e){
        const tapped_index = e.currentTarget.dataset.index;
        //改变激活状态
        let sports_courses = this.handleDownListTapped(tapped_index, this.data.sports_courses);
        this.setData({
            sports_courses:sports_courses
        });
    },
    handleGeneralCoursesDownListTapped(e){
        const tapped_index = e.currentTarget.dataset.index;
        //改变激活状态
        let general_courses = this.handleDownListTapped(tapped_index, this.data.general_courses);
        this.setData({
            general_courses:general_courses
        });
    },
    //获取筛选器中的条件
    getFilterCondition(filter){
        let father_selection = []
        filter.forEach((father_v)=>{
            let children_selection = []
            father_v.content.forEach((children_v)=>{
                if(children_v.isActive){
                    children_selection.push(children_v.name);
                }
            });
            father_selection.push(children_selection);
        });
        return father_selection;
    },
    //获取课程数据
    async getSportsCoursesList(){
        showLoading({"title":"加载中"});
        //获取筛选条件
        let condition = this.getFilterCondition(this.data.sports_courses_filter);
        //清空筛选器
        this.handleSportsCoursesFilterReset();
        //发送请求
        const classroom = condition[0][0]
        const name = condition[1][0]
        this.params.url = "https://u4363536m9.zicp.vip/get/course-list/sports";
        this.params.method = "GET";
        this.params.data["page_number"] = this.sports_courses_page.page_number;
        if(classroom !== undefined){
            this.params.data["classroom"] = classroom;
        }
        if(name !== undefined){
            this.params.data["name"] = name;
        }
        const result = await request(this.params);
        //如果请求出错
        if(result===undefined){
            showToast({"title":"请求超时", "icon":"error"});
            return;
        }
        this.setData({
            sports_courses:[...this.data.sports_courses,...result.data.details]
        });
        //重置参数
        this.params.data = {}
        //页码
        this.sports_courses_page.page_number++;
        wx.setStorageSync("sports_courses", {details:this.data.sports_courses,sports_courses_page:this.sports_courses_page});
        this.sports_courses_page.total_pages = result.data.total_pages;
        wx.hideLoading();
    },
    async getGeneralCoursesList(){
        showLoading({"title":"加载中"});
        //获取筛选条件
        let condition = this.getFilterCondition(this.data.general_courses_filter);
        //清空筛选器
        this.handleGeneralCoursesFilterReset();
        //发送请求
        const credit = condition[0][0]
        const day = condition[1][0]
        const type = condition[2][0]
        this.params.url = "https://u4363536m9.zicp.vip/get/course-list/general";
        this.params.method = "GET";
        this.params.data["page_number"] = this.general_courses_page.page_number;
        if(credit !== undefined){
            this.params.data["credit"] = credit;
        }
        if(day !== undefined){
            this.params.data["day"] = day;
        }
        if(type !== undefined){
            this.params.data["type"] = type;
        }
        const result = await request(this.params);
        //如果请求出错
        if(result===undefined){
            showToast({"title":"请求超时", "icon":"error"});
            return;
        }
        this.setData({
            general_courses:[...this.data.general_courses,...result.data.details]
        });
        wx.setStorageSync("general_courses", this.data.general_courses);
        //重置参数
        this.params.data = {}
        //页码
        this.general_courses_page.total_pages = result.data.total_pages;
        wx.setStorageSync("general_courses", {details:this.data.general_courses,general_courses_page:this.general_courses_page});
        this.general_courses_page.page_number++;
        wx.hideLoading();
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
        const sports_courses = wx.getStorageSync("sports_courses")||{};
        const general_courses = wx.getStorageSync("general_courses")||{};
        if(sports_courses.details===undefined){
            this.getSportsCoursesList();
        }
        if(general_courses.details===undefined){
            this.getGeneralCoursesList();
            return;
        }
        this.setData({
            sports_courses:sports_courses.details
        });
        this.setData({
            general_courses:general_courses.details
        });
        this.sports_courses_page = sports_courses.sports_courses_page;
        this.general_courses_page = general_courses.general_courses_page;
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
        //重置请求参数
        this.params.data = {}
        if(this.data.tabs[0].isActive){
            //重置页数
            this.sports_courses_page = {"total_pages":0, "page_number":1};
            //发送请求
            this.getSportsCoursesList();
        }
        else{
            this.general_courses_page = {"total_pages":0, "page_number":1};
            this.getGeneralCoursesList();
        }
        wx.stopPullDownRefresh();
    },

    /**
     * 页面上拉触底事件的处理函数
     */
    onReachBottom: function () {
        //判断处于页面
        if(this.data.tabs[0].isActive){
            const total_pages = this.sports_courses_page.total_pages;
            const page_number = this.sports_courses_page.page_number;
            if(page_number>=total_pages){
                showToast({"title":"没有更多了", "icon":"error"});
                return;
            }
            this.getSportsCoursesList();
        }
        else{
            const total_pages = this.general_courses_page.total_pages;
            const page_number = this.general_courses_page.page_number;
            if(page_number>=total_pages){
                showToast({"title":"没有更多了", "icon":"error"});
                return;
            }
            this.getGeneralCoursesList();
        }
    },

    /**
     * 用户点击右上角分享
     */
    onShareAppMessage: function () {

    }
})
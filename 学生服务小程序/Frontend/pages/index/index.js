import {request} from "../../request/request.js"
import {showToast} from "../../utils/util.js"

Page({
  data: {
    swiper_list:[
      {
        id:0,
        path:"../../pictures/广州大学服务中心banner1.png"
      },
      {
        id:1,
        path:"../../pictures/广州大学服务中心banner2.png"
      }
    ],
    livelihood_list:[],
    tabs:[
      {
        id:0,
        name:"教学区",
        isActive:true
      },
      {
        id:1,
        name:"服务区",
        isActive:false
      },
      {
        id:2,
        name:"其它",
        isActive:false
      }]
  },
  params:{
    url:'',
    method:'',
    data:{},
    timeout:3000
  },
  handleTabsTappedChange(e){
    const tapped_index = e.detail.tapped_index;
    let tabs = JSON.parse(JSON.stringify(this.data.tabs));
    tabs.forEach((v,i)=>{i==tapped_index?v.isActive=true:v.isActive=false});
    this.setData({
      tabs:tabs
    });
  },
  async getSwiperList(){
    //配置请求参数
    this.params.url='https://u4363536m9.zicp.vip/get/swiper-image';
    this.params.method='GET';
    //发送请求
    const result = await request(this.params);
    if(result===undefined){
      showToast({"title":"请求超时","icon":"error"})
    }
    //将返回的数据储存
    this.setData({
      swiper_list:result.data.details
    });
  },
  async getLivelihoodList(){
    //配置请求参数
    this.params.url='https://u4363536m9.zicp.vip/get/icon';
    this.params.method='GET';
    //发送请求
    const result = await request(this.params);
    //将返回的数据储存
    this.setData({
      livelihood_list:result.data.details
    });
  },
  onLoad: function (options) {
    // this.getSwiperList();
    // this.getLivelihoodList();
}
})

export const showLoading=(async ({"title":title})=>{
    return new Promise((resolve, reject) => {
        wx.showLoading({
            title: title,
            mask: true,
            success: (result) => {
                resolve(result);
            },
            fail: (error) => {
                reject(error);
            }
        });
    }).catch (error =>{
        console.log(error);
    });
});

export const showToast=(async ({"title":title,"icon":icon})=>{
    return new Promise((resovle, reject) => {
        wx.showToast({
            title: title,
            icon: icon,
            duration: 1500,
            mask: true,
            success: (result) => {
                resovle(result);
            },
            fail: (error) => {
                reject(error);
            }
        });
    }).catch (error =>{
        console.log(error);
    });
});

export const showModal=(async ({"title":title,"content":content})=>{
    return new Promise((resovle, reject) => {
        wx.showModal({
            title: title,
            content: content,
            showCancel: true,
            confirmText: '确定',
            confirmColor: '#007acc',
            success: (result) => {
                resovle(result);
            },
            fail: (error) => {
                reject(error);
            }
        });
    }).catch (error =>{
        console.log(error);
    });
});

export const getUserProfile=(async ({"desc":desc})=>{
    return new Promise((resolve, reject) => {
        wx.getUserProfile({
            desc: desc,
            success: (result) => {
                resolve(result);
            },
            fail: (error) => {
                reject(error);
            }
        });
    }).catch (error =>{
        console.log(error);
    });
});

export const chooseImage=(async ()=>{
    return new Promise((resolve, reject) => {
        wx.chooseImage({
            count: 9,
            sizeType: ['original', 'compressed'],
            sourceType: ['album', 'camera'],
            success: (result) => {
                resolve(result);
            },
            fail: (error) => {
                reject(error);
            }
        });
    }).catch (error =>{
        console.log(error);
    });
});

export const uploadFile=(async ({"filePath":filePath,"formData":formData})=>{
    return new Promise((resolve, reject) => {
        wx.uploadFile({
            url: 'https://u4363536m9.zicp.vip/add/feedback',
            filePath: filePath,
            name: "feedback_image",
            formData: formData,
            timeout:1000,
            success: (result) =>{
                resolve(result);
            },
            fail: (error) =>{
                reject(error);
            }
        });
    }).catch (error=>{
        console.log(error);
    });
});
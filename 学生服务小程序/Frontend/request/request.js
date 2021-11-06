export const request=(async (params)=>{
    return new Promise((resolve, reject) => {
        wx.request({
            ...params,
            url: params.url,
            data: params.data,
            timeout: params.timeout,
            method: params.method,
            dataType: "json",
            success: (result) => {
                resolve(result);
            },
            fail: (error) => {
                reject(error);
            }
        });
    }).catch(error=>{
        console.log(error);
    });
})
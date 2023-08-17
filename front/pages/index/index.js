Page({
  /**
   * 页面的初始数据
   */
  data: {
    inputAction: false,
    questionInfo: '',
    hotQuestions: ['学校可以带电器吗', '校内有无快递站', '宿舍是上床下桌吗'],
    contentInfo: [],
    sendFlag: true,
    inputFlag: false,
    ScrollTop: 0,
    bottom: '',
    // 存放接收到的流式数据
    receivedData: '',
    // 存放逐字显示的数据
    displayedData: '',
    // 定义一个显示数据的定时器
    showTimer: null,
    // WebSocket 连接状态
    websocketConnected: false,
    // 手动关闭websocket的标识
    handleCloseWS: false,
    answerLoadingInfo: false,
    // 当前最后一个元素的时间
    currentTime: ''
  },



  // 聚焦输入框
  onTabInput(event) {
    console.log('触发')
    this.setData({
      inputAction: true
    })
  },

  // 失去聚焦输入框
  offTabInput(event) {
    console.log('触发')
    this.setData({
      inputAction: false
    })
  },

  // 点击热门问题
  onTabHot(event) {
    this.onTabInput()
    const questionInfo = event.currentTarget.id
    this.setData({ questionInfo })
    // 开启连接
    this.connectWebSocket()
  },


  // 发送问题  --websocket 流式数据传输
  onSendQuestion() {
    const contentInfo = this.data.contentInfo
    const questionInfo = this.data.questionInfo.trim()
    if (this.data.sendFlag) {
      this.data.sendFlag = false
      if (!questionInfo) {
        wx.showToast({
          title: '请输入问题',
          icon: 'none'
        })
      } else {
        this.setData({
          inputFlag: true
        })
        // 连接建立后，发送问题给后端
        wx.sendSocketMessage({
          // data: JSON.stringify(`${questionInfo}`)
          data: questionInfo
        }).then(res => {
          console.log('zhangshiyi', res)
          const currentTime = this.setProtoTime()
          contentInfo?.push({
            question: questionInfo,
            answer: '',
            time: currentTime
          })
          // console.log(contentInfo)
          this.setData({
            contentInfo,
            // inputAction: false
            bottom: 'scrollBottom',
            currentTime
          })
        })
      }
      setTimeout(() => {
        this.data.sendFlag = true
      }, 1000)
    } else {
      wx.showToast({
        title: '请勿频繁点击',
        icon: 'error'
      })
    }
  },

  // 设置时间的函数
  setProtoTime() {
    const time = new Date()
    let yyyy = time.getFullYear()
    let MM = String(time.getMonth() + 1).padStart(2, '0')
    let DD = String(time.getDate()).padStart(2, '0')
    let hh = String(time.getHours()).padStart(2, '0') //获取当前小时数(0-23)
    let mm = String(time.getMinutes()).padStart(2, '0') //获取当前分钟数(0-59)
    let ss = String(time.getSeconds()).padStart(2, '0') //获取当前秒数(0-59)
    return yyyy + '-' + MM + '-' + DD + ' ' + hh + ':' + mm + ':' + ss
  },

  // 删除的回调
  removeAnswer(event) {
    // 删除分成4种情况
    // 1. 没建立连接时，点击删除，删除本地
    // 2. 建立连接，没发送请求，点击删除，删除本地
    // 3. 建立连接，已发送请求，点击删除不是响应中的数据，删除本地
    // 4. 建立连接，已发送请求，点击删除响应中的数据，清空输入框，断连接 --> 数据回显，变量handleCloseWS
    const removeItemTime = event.currentTarget.id
    const contentInfo = this.data.contentInfo
    // const currentShowItem = contentInfo.slice(-1)[0].time
    const currentShowItem = this.data.currentTime

    if (this.data.inputFlag && removeItemTime === currentShowItem) {
      // 手动关闭ws
      this.closeWebSocket()
      // console.log(contentInfo)
      // contentInfo.pop()
      this.setData({
        questionInfo: '',
        inputFlag: false,
        // contentInfo,
        handleCloseWS: true,
        displayedData: '',
        receivedData: '',
        inputAction: false
      })
      // 避免删除正在展示的数据时同时清除前面数据的bug
      setTimeout(() => {
        const contentInfo = this.data.contentInfo
        // console.log(contentInfo)
        contentInfo.pop()
        this.setData({ contentInfo })
      }, 500)
    } else {
      const newContentInfo = this.data.contentInfo.filter((item, index) => {
        return item.time !== removeItemTime
      })
      this.setData({
        contentInfo: newContentInfo
      })
      wx.setStorageSync('questionInfo', newContentInfo)
    }
  },

  // 初始化获取本地数据
  async initializeLocalData(time = 7) {
    const currentTime = new Date().getTime()
    // console.log("当前时间", currentTime);
    const saveTime = time * 24 * 60 * 60 * 1000
    // console.log("保存时间", saveTime);
    const result = wx.getStorageSync('questionInfo')
    const newContentInfo = result.filter((item, index) => {
      let itemTime = new Date(item.time).getTime()
      return currentTime - itemTime < saveTime
    })
    console.log('没到期的问题', newContentInfo)
    this.setData({
      contentInfo: newContentInfo
    })
    wx.setStorageSync('questionInfo', newContentInfo)
    // const newQuestionInfo = [...this.data.contentInfo, ...oldQuestionInfo]
    // 每次更新bottom，保证#scrollBottom每次都是最后一个元素

    if (newContentInfo.length) {
      wx.nextTick(() => {
        this.setData({
          bottom: 'scrollBottom'
        })
      })
    }
  },

  // 建立 WebSocket 连接
  connectWebSocket() {
    if (this.data.websocketConnected) return
    wx.connectSocket({
      url: 'ws://127.0.0.1:8000/ask', //上线需要wss协议
      // header: {
      //   'content-type': 'application/json'
      // },
      success: () => {
        console.log('WebSocket连接成功')
        this.setData({ websocketConnected: true, handleCloseWS: false })
        this.initEventHandle()
      },
      fail: err => {
        // console.log("连接失败")
        console.error('WebSocket连接失败', err)
      }
    })
  },

  // 监听webSocket链接
  initEventHandle() {
    // 监听 WebSocket 接收到的消息
    wx.onSocketMessage(res => {
      // res.data 就是接收到的流式数据
      // 将接收到的数据保存到全局变量 receivedData 中
      // console.log(res)
      this.setData({
        receivedData: this.data.receivedData + res.data
      })
      // 模拟每隔一定时间逐字显示数据
      this.showDataOneByOne()
    })
    wx.onSocketOpen(() => {
      console.log('WebSocket连接打开')
    })
    wx.onSocketError(res => {
      console.log('WebSocket连接打开失败')
    })
    wx.onSocketClose(res => {
      this.setData({
        websocketConnected: false
      })
      console.log('WebSocket 已关闭！')
    })
  },

  // 关闭 WebSocket 连接,手动
  closeWebSocket() {
    wx.closeSocket({
      code: 1000, // 设置状态码为 1000
      reason: '手动关闭ws',
      success: () => {
        console.log('WebSocket连接手动关闭成功')
      },
      fail: err => {
        console.log('WebSocket连接手动关闭失败', err)
      }
    })
  },

  // 定义逐字显示数据的函数
  showDataOneByOne() {
    // 手动关闭了websocket不能再进入,也即不能在页面内显示内容
    if (this.data.handleCloseWS) return

    // 如果定时器已经存在，则清除之前的定时器
    if (this.data.showTimer) {
      clearTimeout(this.data.showTimer)
    }

    // 设置定时器，在一定时间间隔后显示一个字
    this.data.showTimer = setTimeout(() => {
      // 获取当前已经显示的数据长度
      const currentLength = this.data.displayedData.length

      // 获取下一个要显示的字符
      const nextChar = this.data.receivedData.charAt(currentLength)

      // 在页面上显示的下一个字符
      // this.setData({ displayedData: this.data.displayedData + nextChar })
      this.data.displayedData += nextChar
      const contentInfo = this.data.contentInfo
      const lastItem = contentInfo[contentInfo.length - 1]
      lastItem.answer = this.data.displayedData
      // 更改contentInfo中的数据进行修改
      this.setData({
        contentInfo,
        bottom: 'scrollBottom'
      })

      // websoket关闭，且数据响应结束重置数据并保存本地
      if (this.data.displayedData === this.data.receivedData && this.data.websocketConnected == false) {
        if (this.data.contentInfo.slice(-1)[0].answer) {
          wx.setStorageSync('questionInfo', this.data.contentInfo)
        }
        this.setData({
          questionInfo: '',
          inputFlag: false,
          displayedData: '',
          receivedData: '',
          inputAction: false
        })
      }

      // 判断是否还有字符未显示完，如果有，继续递归调用 showDataOneByOne
      if (currentLength < this.data.receivedData.length) {
        this.showDataOneByOne()
      }
    }, 80) // 这里的 80 毫秒可以根据需要调整，控制每个字符的显示速度
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    // 建立websocket连接
    // this.connectWebSocket()
    // 初始化获取本地的问题
    this.initializeLocalData()

    wx.showShareMenu({
      withShareTicket: true, // 是否使用带 shareTicket 的转发
      menu: ['shareAppMessage', 'shareTimeline'] // 显示的分享菜单项
    })
  },
  onShareAppMessage: function () {
    return {
      title: 'We校园-新生问答' // 分享标题
    }
  }
})

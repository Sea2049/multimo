/**
 * 临时存储待上传的文件和需求
 * 用于首页点击启动引擎后立即跳转，在Process页面再进行API调用
 */
import { reactive } from 'vue'

const state = reactive({
  files: [],
  simulationRequirement: '',
  mode: 'auto', // 默认为自动驾驶
  rounds: 15,   // 默认模拟轮数
  isPending: false
})

export function setPendingUpload(files, requirement, mode = 'auto', rounds = 15) {
  state.files = files
  state.simulationRequirement = requirement
  state.mode = mode
  state.rounds = rounds
  state.isPending = true
}

export function getPendingUpload() {
  return {
    files: state.files,
    simulationRequirement: state.simulationRequirement,
    mode: state.mode,
    rounds: state.rounds,
    isPending: state.isPending
  }
}

export function clearPendingUpload() {
  state.files = []
  state.simulationRequirement = ''
  state.mode = 'auto'
  state.rounds = 15
  state.isPending = false
}

export default state

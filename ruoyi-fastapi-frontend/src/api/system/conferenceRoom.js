import request from '@/utils/request'

export function listConferenceRoom(query) {
  return request({
    url: '/system/conferenceRoom/list',
    method: 'get',
    params: query
  })
}

export function getConferenceRoom(roomId) {
  return request({
    url: '/system/conferenceRoom/' + roomId,
    method: 'get'
  })
}

export function addConferenceRoom(data) {
  return request({
    url: '/system/conferenceRoom',
    method: 'post',
    data: data
  })
}

export function updateConferenceRoom(data) {
  return request({
    url: '/system/conferenceRoom',
    method: 'put',
    data: data
  })
}

export function delConferenceRoom(roomIds) {
  return request({
    url: '/system/conferenceRoom/' + roomIds,
    method: 'delete'
  })
}

export function changeConferenceRoomStatus(roomId, status) {
  const data = {
    roomId,
    status
  }
  return request({
    url: '/system/conferenceRoom/changeStatus',
    method: 'put',
    data: data
  })
}

export function exportConferenceRoom(query) {
  return request({
    url: '/system/conferenceRoom/export',
    method: 'post',
    data: query
  })
}

export function listConferenceRoomLayout(roomId) {
  return request({
    url: '/system/conferenceRoom/layout/list/' + roomId,
    method: 'get'
  })
}

export function getConferenceRoomLayout(layoutId) {
  return request({
    url: '/system/conferenceRoom/layout/' + layoutId,
    method: 'get'
  })
}

export function addConferenceRoomLayout(data) {
  return request({
    url: '/system/conferenceRoom/layout',
    method: 'post',
    data: data
  })
}

export function updateConferenceRoomLayout(data) {
  return request({
    url: '/system/conferenceRoom/layout',
    method: 'put',
    data: data
  })
}

export function delConferenceRoomLayout(layoutIds) {
  return request({
    url: '/system/conferenceRoom/layout/' + layoutIds,
    method: 'delete'
  })
}

export function getConferenceRoomLayoutByRoomId(roomId) {
  return request({
    url: `/system/conferenceRoom/layout/room/${roomId}`,
    method: 'get'
  })
}

export function saveConferenceRoomLayout(data) {
  return request({
    url: '/system/conferenceRoom/layout/save',
    method: 'post',
    data: data
  })
}
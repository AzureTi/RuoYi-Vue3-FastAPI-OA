import request from '@/utils/request'

export function listMeeting(query) {
  return request({
    url: '/system/meeting/list',
    method: 'get',
    params: query
  })
}

export function getMeeting(meetingId) {
  return request({
    url: '/system/meeting/' + meetingId,
    method: 'get'
  })
}

export function addMeeting(data) {
  return request({
    url: '/system/meeting',
    method: 'post',
    data: data
  })
}

export function updateMeeting(data) {
  return request({
    url: '/system/meeting',
    method: 'put',
    data: data
  })
}

export function delMeeting(meetingIds) {
  return request({
    url: '/system/meeting/' + meetingIds,
    method: 'delete'
  })
}

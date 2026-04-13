<template>
  <div class="app-container">
    <el-form
      :model="queryParams"
      ref="queryRef"
      :inline="true"
      v-show="showSearch"
      label-width="90px"
    >
      <el-form-item label="会议名称" prop="meetingName">
        <el-input
          v-model="queryParams.meetingName"
          placeholder="请输入会议名称"
          clearable
          style="width: 240px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="会议状态" prop="status">
        <el-select
          v-model="queryParams.status"
          placeholder="会议状态"
          clearable
          style="width: 240px"
        >
          <el-option
            v-for="dict in meeting_status"
            :key="dict.value"
            :label="dict.label"
            :value="dict.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="创建时间" style="width: 308px">
        <el-date-picker
          v-model="dateRange"
          value-format="YYYY-MM-DD"
          type="daterange"
          range-separator="-"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
        ></el-date-picker>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery"
          >搜索</el-button
        >
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button
          type="primary"
          plain
          icon="Plus"
          @click="handleAdd"
          v-hasPermi="['system:meeting:add']"
          >新增</el-button
        >
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="success"
          plain
          icon="Edit"
          :disabled="single"
          @click="handleUpdate"
          v-hasPermi="['system:meeting:edit']"
          >修改</el-button
        >
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="danger"
          plain
          icon="Delete"
          :disabled="multiple"
          @click="handleDelete"
          v-hasPermi="['system:meeting:remove']"
          >删除</el-button
        >
      </el-col>
      <right-toolbar
        v-model:showSearch="showSearch"
        @queryTable="getList"
        :columns="columns"
      ></right-toolbar>
    </el-row>

    <el-table
      v-loading="loading"
      :data="meetingList"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="50" align="center" />
      <el-table-column
        label="会议编号"
        align="center"
        key="meetingId"
        prop="meetingId"
        v-if="columns.meetingId.visible"
      />
      <el-table-column
        label="会议名称"
        align="center"
        key="meetingName"
        prop="meetingName"
        v-if="columns.meetingName.visible"
        :show-overflow-tooltip="true"
      />
      <el-table-column
        label="主会场"
        align="center"
        key="mainRoomName"
        prop="mainRoomName"
        v-if="columns.mainRoomName.visible"
        :show-overflow-tooltip="true"
      />
      <el-table-column
        label="开始时间"
        align="center"
        key="startTime"
        prop="startTime"
        v-if="columns.startTime.visible"
        width="160"
      >
        <template #default="scope">
          <span>{{ parseTime(scope.row.startTime) }}</span>
        </template>
      </el-table-column>
      <el-table-column
        label="时长(分钟)"
        align="center"
        key="duration"
        prop="duration"
        v-if="columns.duration.visible"
      />
      <el-table-column
        label="会议状态"
        align="center"
        key="status"
        v-if="columns.status.visible"
      >
        <template #default="scope">
          <el-tag :type="getStatusTagType(scope.row.status)">
            {{ getStatusLabel(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column
        label="创建时间"
        align="center"
        prop="createTime"
        v-if="columns.createTime.visible"
        width="160"
      >
        <template #default="scope">
          <span>{{ parseTime(scope.row.createTime) }}</span>
        </template>
      </el-table-column>
      <el-table-column
        label="操作"
        align="center"
        width="150"
        class-name="small-padding fixed-width"
      >
        <template #default="scope">
          <el-tooltip content="修改" placement="top">
            <el-button
              link
              type="primary"
              icon="Edit"
              @click="handleUpdate(scope.row)"
              v-hasPermi="['system:meeting:edit']"
            ></el-button>
          </el-tooltip>
          <el-tooltip content="删除" placement="top">
            <el-button
              link
              type="primary"
              icon="Delete"
              @click="handleDelete(scope.row)"
              v-hasPermi="['system:meeting:remove']"
            ></el-button>
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>
    <pagination
      v-show="total > 0"
      :total="total"
      v-model:page="queryParams.pageNum"
      v-model:limit="queryParams.pageSize"
      @pagination="getList"
    />

    <!-- 添加或修改会议对话框 -->
    <el-dialog :title="title" v-model="open" width="700px" append-to-body>
      <el-form :model="form" :rules="rules" ref="meetingRef" label-width="100px">
        <el-row>
          <el-col :span="24">
            <el-form-item label="会议名称" prop="meetingName">
              <el-input
                v-model="form.meetingName"
                placeholder="请输入会议名称"
                maxlength="100"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="12">
            <el-form-item label="组织部门" prop="deptId">
              <el-tree-select
                v-model="form.deptId"
                :data="deptOptions"
                :props="{ value: 'id', label: 'label', children: 'children' }"
                value-key="id"
                placeholder="请选择组织部门"
                check-strictly
                clearable
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系人" prop="organizerId">
              <el-select
                v-model="form.organizerId"
                placeholder="请选择联系人"
                clearable
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="user in userOptions"
                  :key="user.userId"
                  :label="user.nickName"
                  :value="user.userId"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="24">
            <el-form-item label="主会场" prop="mainRoomId">
              <el-select
                v-model="form.mainRoomId"
                placeholder="请选择主会场（可选）"
                clearable
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="room in mainRoomOptions"
                  :key="room.roomId"
                  :label="room.roomName"
                  :value="room.roomId"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="24">
            <el-form-item label="分会场" prop="subRooms">
              <el-select
                v-model="subRoomIds"
                multiple
                placeholder="请选择分会场（可选，可多选）"
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="room in subRoomOptions"
                  :key="room.roomId"
                  :label="room.roomName"
                  :value="room.roomId"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="24">
            <el-form-item label="开始时间" prop="startTime">
              <div style="display: flex; width: 100%; gap: 10px;">
                <el-date-picker
                  v-model="startDate"
                  type="date"
                  placeholder="选择日期"
                  value-format="YYYY-MM-DD"
                  style="flex: 1;"
                  @change="updateStartTime"
                />
                <el-select
                  v-model="startTimeValue"
                  placeholder="选择时间"
                  filterable
                  allow-create
                  default-first-option
                  style="flex: 1;"
                  @change="updateStartTime"
                >
                  <el-option
                    v-for="time in timeOptions"
                    :key="time"
                    :label="time"
                    :value="time"
                  />
                </el-select>
              </div>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="12">
            <el-form-item label="时长(分钟)" prop="duration">
              <el-input-number
                v-model="form.duration"
                :min="1"
                :max="1440"
                placeholder="请输入时长"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="24">
            <el-form-item label="备注">
              <el-input
                v-model="form.remark"
                type="textarea"
                placeholder="请输入内容"
              ></el-input>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="submitForm">确 定</el-button>
          <el-button @click="cancel">取 消</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="Meeting">
import {
  listMeeting,
  getMeeting,
  addMeeting,
  updateMeeting,
  delMeeting
} from "@/api/system/meeting";
import { listConferenceRoom } from "@/api/system/conferenceRoom";
import { deptTreeSelect, listUser } from "@/api/system/user";
import useUserStore from "@/store/modules/user";

import { ref, reactive, toRefs, onMounted, getCurrentInstance, computed } from 'vue';

const { proxy } = getCurrentInstance();
const userStore = useUserStore();

const meetingList = ref([]);
const open = ref(false);
const loading = ref(true);
const showSearch = ref(true);
const ids = ref([]);
const single = ref(true);
const multiple = ref(true);
const total = ref(0);
const title = ref("");
const dateRange = ref([]);
const roomOptions = ref([]);
const subRoomIds = ref([]);
const startDate = ref(null);
const startTimeValue = ref(null);
const deptOptions = ref([]);
const userOptions = ref([]);

const timeOptions = [];
for (let h = 0; h < 24; h++) {
  for (let m = 0; m < 60; m += 15) {
    timeOptions.push(`${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`);
  }
}

const meeting_status = ref([
  { value: '0', label: '草稿' },
  { value: '1', label: '待审核' },
  { value: '2', label: '已通过' },
  { value: '3', label: '进行中' },
  { value: '4', label: '已结束' },
]);

const columns = ref({
  meetingId: { label: "会议编号", visible: false },
  meetingName: { label: "会议名称", visible: true },
  mainRoomName: { label: "主会场", visible: true },
  startTime: { label: "开始时间", visible: true },
  duration: { label: "时长(分钟)", visible: true },
  status: { label: "会议状态", visible: true },
  createTime: { label: "创建时间", visible: true },
});

const data = reactive({
  form: {},
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    meetingName: undefined,
    status: undefined,
  },
  rules: {
    meetingName: [
      { required: true, message: "会议名称不能为空", trigger: "blur" },
      { min: 1, max: 100, message: "会议名称长度必须介于 1 和 100 之间", trigger: "blur" },
    ],
    startTime: [
      { required: true, message: "开始时间不能为空", trigger: "blur" },
    ],
    duration: [
      { required: true, message: "时长不能为空", trigger: "blur" },
      { type: "number", min: 1, message: "时长必须大于 0", trigger: "blur" },
    ],
  },
});

const { queryParams, form, rules } = toRefs(data);

const subRoomOptions = computed(() => {
  return roomOptions.value.filter(room => room.roomId !== form.value.mainRoomId);
});

const mainRoomOptions = computed(() => {
  return roomOptions.value.filter(room => !subRoomIds.value.includes(room.roomId));
});

function getStatusLabel(status) {
  const statusDict = meeting_status.value.find(d => d.value === status);
  return statusDict ? statusDict.label : '未知';
}

function getStatusTagType(status) {
  const typeMap = {
    '0': 'info',
    '1': 'warning',
    '2': 'success',
    '3': 'primary',
    '4': 'default',
  };
  return typeMap[status] || 'info';
}

function getList() {
  loading.value = true;
  listMeeting(proxy.addDateRange(queryParams.value, dateRange.value)).then(
    (res) => {
      loading.value = false;
      meetingList.value = res.rows;
      total.value = res.total;
    }
  );
}

function handleQuery() {
  queryParams.value.pageNum = 1;
  getList();
}

function resetQuery() {
  dateRange.value = [];
  proxy.resetForm("queryRef");
  handleQuery();
}

function handleDelete(row) {
  const meetingIds = row.meetingId || ids.value;
  proxy.$modal
    .confirm('是否确认删除会议编号为"' + meetingIds + '"的数据项？')
    .then(function () {
      return delMeeting(meetingIds);
    })
    .then(() => {
      getList();
      proxy.$modal.msgSuccess("删除成功");
    })
    .catch(() => {});
}

function handleSelectionChange(selection) {
  ids.value = selection.map((item) => item.meetingId);
  single.value = selection.length != 1;
  multiple.value = !selection.length;
}

function updateStartTime() {
  if (startDate.value && startTimeValue.value) {
    form.value.startTime = `${startDate.value} ${startTimeValue.value}:00`;
  } else if (startDate.value) {
    form.value.startTime = `${startDate.value} 08:00:00`;
  } else {
    form.value.startTime = undefined;
  }
}

function reset() {
  const today = new Date();
  const defaultDate = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
  startDate.value = defaultDate;
  startTimeValue.value = '08:00';
  form.value = {
    meetingId: undefined,
    meetingName: undefined,
    deptId: userStore.deptId,
    mainRoomId: undefined,
    subRooms: undefined,
    startTime: `${defaultDate} 08:00:00`,
    duration: 60,
    status: '0',
    organizerId: userStore.id,
    remark: undefined,
  };
  subRoomIds.value = [];
  proxy.resetForm("meetingRef");
}

function cancel() {
  open.value = false;
  reset();
}

function handleAdd() {
  reset();
  open.value = true;
  title.value = "添加会议";
}

function handleUpdate(row) {
  reset();
  const meetingId = row.meetingId || ids.value;
  getMeeting(meetingId).then((response) => {
    form.value = response.data.data;
    if (form.value.startTime) {
      let dateTimeStr = form.value.startTime;
      if (dateTimeStr.includes('T')) {
        const parts = dateTimeStr.split('T');
        startDate.value = parts[0];
        if (parts[1]) {
          startTimeValue.value = parts[1].substring(0, 5);
        } else {
          startTimeValue.value = '08:00';
        }
      } else if (dateTimeStr.includes(' ')) {
        const dateTime = dateTimeStr.split(' ');
        startDate.value = dateTime[0];
        if (dateTime[1]) {
          startTimeValue.value = dateTime[1].substring(0, 5);
        } else {
          startTimeValue.value = '08:00';
        }
      }
    }
    if (form.value.subRooms) {
      subRoomIds.value = form.value.subRooms.split(',').map(id => parseInt(id)).filter(id => !isNaN(id));
    } else {
      subRoomIds.value = [];
    }
    open.value = true;
    title.value = "修改会议";
  });
}

function submitForm() {
  proxy.$refs["meetingRef"].validate((valid) => {
    if (valid) {
      if (subRoomIds.value && subRoomIds.value.length > 0) {
        form.value.subRooms = subRoomIds.value.join(',');
      } else {
        form.value.subRooms = undefined;
      }
      if (form.value.meetingId != undefined) {
        updateMeeting(form.value).then((response) => {
          proxy.$modal.msgSuccess("修改成功");
          open.value = false;
          getList();
        });
      } else {
        addMeeting(form.value).then((response) => {
          proxy.$modal.msgSuccess("新增成功");
          open.value = false;
          getList();
        });
      }
    }
  });
}

function getRoomOptions() {
  listConferenceRoom({ pageNum: 1, pageSize: 1000, status: '0' }).then((response) => {
    roomOptions.value = response.rows;
  });
}

function getDeptTree() {
  deptTreeSelect().then((response) => {
    deptOptions.value = response.data;
  });
}

function getUserList() {
  listUser({ pageNum: 1, pageSize: 1000, status: '0' }).then((response) => {
    userOptions.value = response.rows;
  });
}

onMounted(() => {
  getList();
  getRoomOptions();
  getDeptTree();
  getUserList();
});
</script>

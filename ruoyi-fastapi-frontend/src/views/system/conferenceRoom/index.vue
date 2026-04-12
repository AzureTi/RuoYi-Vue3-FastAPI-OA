<template>
  <div class="app-container">
    <el-form
      :model="queryParams"
      ref="queryRef"
      :inline="true"
      v-show="showSearch"
      label-width="90px"
    >
      <el-form-item label="会议室名称" prop="roomName">
        <el-input
          v-model="queryParams.roomName"
          placeholder="请输入会议室名称"
          clearable
          style="width: 240px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="位置" prop="location">
        <el-input
          v-model="queryParams.location"
          placeholder="请输入会议室位置"
          clearable
          style="width: 240px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-select
          v-model="queryParams.status"
          placeholder="会议室状态"
          clearable
          style="width: 240px"
        >
          <el-option
            v-for="dict in sys_normal_disable"
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
          v-hasPermi="['system:conferenceRoom:add']"
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
          v-hasPermi="['system:conferenceRoom:edit']"
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
          v-hasPermi="['system:conferenceRoom:remove']"
          >删除</el-button
        >
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="warning"
          plain
          icon="Download"
          @click="handleExport"
          v-hasPermi="['system:conferenceRoom:export']"
          >导出</el-button
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
      :data="conferenceRoomList"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="50" align="center" />
      <el-table-column
        label="会议室编号"
        align="center"
        key="roomId"
        prop="roomId"
        v-if="columns.roomId.visible"
      />
      <el-table-column
        label="会议室名称"
        align="center"
        key="roomName"
        prop="roomName"
        v-if="columns.roomName.visible"
        :show-overflow-tooltip="true"
      />
      <el-table-column
        label="容纳人数"
        align="center"
        key="capacity"
        prop="capacity"
        v-if="columns.capacity.visible"
      />
      <el-table-column
        label="位置"
        align="center"
        key="location"
        prop="location"
        v-if="columns.location.visible"
        :show-overflow-tooltip="true"
      />
      <el-table-column
        label="设备配置"
        align="center"
        key="equipment"
        prop="equipment"
        v-if="columns.equipment.visible"
        :show-overflow-tooltip="true"
      />
      <el-table-column
        label="标签"
        align="center"
        key="tags"
        prop="tags"
        v-if="columns.tags.visible"
        :show-overflow-tooltip="true"
      />
      <el-table-column
        label="状态"
        align="center"
        key="status"
        v-if="columns.status.visible"
      >
        <template #default="scope">
          <el-switch
            v-model="scope.row.status"
            active-value="0"
            inactive-value="1"
            @change="handleStatusChange(scope.row)"
          ></el-switch>
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
          <el-tooltip
            content="修改"
            placement="top"
          >
            <el-button
              link
              type="primary"
              icon="Edit"
              @click="handleUpdate(scope.row)"
              v-hasPermi="['system:conferenceRoom:edit']"
            ></el-button>
          </el-tooltip>
          <el-tooltip
            content="删除"
            placement="top"
          >
            <el-button
              link
              type="primary"
              icon="Delete"
              @click="handleDelete(scope.row)"
              v-hasPermi="['system:conferenceRoom:remove']"
            ></el-button>
          </el-tooltip>
          <el-tooltip
            content="设置会议室布局"
            placement="top"
          >
            <el-button
              link
              type="primary"
              icon="Setting"
              @click="handleLayout(scope.row)"
              v-hasPermi="['system:conferenceRoom:edit']"
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

    <!-- 添加或修改会议室配置对话框 -->
    <el-dialog :title="title" v-model="open" width="600px" append-to-body>
      <el-form :model="form" :rules="rules" ref="conferenceRoomRef" label-width="100px">
        <el-row>
          <el-col :span="12">
            <el-form-item label="会议室名称" prop="roomName">
              <el-input
                v-model="form.roomName"
                placeholder="请输入会议室名称"
                maxlength="50"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="容纳人数" prop="capacity">
              <el-input
                v-model.number="form.capacity"
                placeholder="请输入容纳人数"
                type="number"
                min="1"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="24">
            <el-form-item label="位置" prop="location">
              <el-input
                v-model="form.location"
                placeholder="请输入会议室位置"
                maxlength="100"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="24">
            <el-form-item label="会议设备" prop="equipment">
              <el-input
                v-model="form.equipment"
                placeholder="请输入会议设备"
                maxlength="200"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="12">
            <el-form-item label="标签" prop="tags">
              <el-input
                v-model="form.tags"
                placeholder="请输入标签，多个标签用逗号分隔"
                maxlength="200"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-radio-group v-model="form.status">
                <el-radio
                  v-for="dict in sys_normal_disable"
                  :key="dict.value"
                  :value="dict.value"
                  >{{ dict.label }}</el-radio
                >
              </el-radio-group>
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

    <!-- 会议室布局设置对话框 -->
    <el-dialog :title="layoutTitle" v-model="layoutOpen" width="90%" append-to-body :class="{ 'layout-dialog-maximized': isMaximized }">
      <div class="layout-editor">
        <div class="layout-config" v-if="!isMaximized">
          <h3>布局配置</h3>
          <div class="config-form-row">
            <div class="form-group">
              <label>主席台样式</label>
              <el-select v-model="layoutConfig.podiumStyle" @change="updateLayout">
                <el-option value="bar" label="条形桌"></el-option>
                <el-option value="round" label="圆形桌"></el-option>
              </el-select>
            </div>
            <div class="form-group">
              <label>排数</label>
              <el-input-number v-model="layoutConfig.rows" :min="1" :max="20" @change="updateLayout"></el-input-number>
            </div>
            <div class="form-group">
              <label>列数</label>
              <el-input-number v-model="layoutConfig.columns" :min="1" :max="40" @change="updateLayout"></el-input-number>
            </div>
            <div class="form-group">
              <label>座位号编排</label>
              <el-select v-model="layoutConfig.seatNumberType" @change="updateSeatLayout">
                <el-option value="odd-even" label="左奇右偶"></el-option>
                <el-option value="even-odd" label="左偶右奇"></el-option>
                <el-option value="sequential" label="左右顺序"></el-option>
                <el-option value="reverse" label="左右逆序"></el-option>
              </el-select>
            </div>
            <div class="form-group">
              <label>通道数量</label>
              <el-input-number v-model="layoutConfig.aisleCount" :min="0" :max="5" @change="updateLayout"></el-input-number>
            </div>
            <div class="form-group" v-if="layoutConfig.aisleCount > 0">
              <label>通道位置</label>
              <div v-for="i in layoutConfig.aisleCount" :key="i" class="aisle-position-item">
                <label>通道{{ i }}方向：</label>
                <el-select :id="`aisle-direction-${i}`" v-model="layoutConfig.aisles[i-1].direction" @change="updateLayout" style="width: 90px;">
                  <el-option value="vertical" label="纵向"></el-option>
                  <el-option value="horizontal" label="横向"></el-option>
                </el-select>
                <label>位置：</label>
                <el-select :id="`aisle-position-${i}`" v-model="layoutConfig.aisles[i-1].position" @change="updateLayout" style="width: 180px;">
                  <el-option value="auto" label="自动"></el-option>
                  <template v-if="layoutConfig.aisles[i-1].direction === 'vertical'">
                    <el-option v-for="pos in layoutConfig.columns - 1" :key="pos" :value="pos" :label="getAislePositionLabel(pos)"></el-option>
                  </template>
                  <template v-else>
                    <el-option v-for="pos in layoutConfig.rows - 1" :key="pos" :value="pos" :label="`${pos}排和${pos+1}排之间`"></el-option>
                  </template>
                </el-select>
              </div>
            </div>
          </div>
          <div class="config-actions-row">
            <div class="layout-legend">
              <p><span class="seat-legend available"></span> 可用座位</p>
              <p><span class="seat-legend unavailable"></span> 不可用座位</p>
              <p><span class="seat-legend screen"></span> 主席台</p>
            </div>
            <div class="show-thumbnail-option">
              <el-checkbox v-model="layoutConfig.showThumbnail" @change="toggleThumbnail">显示缩略图</el-checkbox>
            </div>
          </div>
        </div>
        
        <div class="layout-thumbnail-section" v-if="layoutConfig.showThumbnail && !isMaximized">
          <h3>缩略图</h3>
          <div id="thumbnail-container" class="thumbnail-container">
            <div class="thumbnail-grid">
              <template v-for="(row, rowIndex) in seatLayout" :key="rowIndex">
                <div class="thumbnail-row">
                  <template v-for="(seat, colIndex) in row" :key="colIndex">
                    <div class="thumbnail-seat" :class="{ available: seat.available, unavailable: !seat.available }"></div>
                    <template v-for="aisle in layoutConfig.aisles" :key="`aisle-${rowIndex}-${aisle?.aisleNumber || rowIndex}`">
                      <div v-if="aisle && aisle.direction === 'vertical' && aisle.position > 0 && aisle.position === colIndex + 1" class="thumbnail-aisle"></div>
                    </template>
                  </template>
                </div>
                <template v-for="(aisle, aisleIdx) in layoutConfig.aisles" :key="`h-aisle-${rowIndex}-${aisle?.aisleNumber || aisleIdx}`">
                  <div v-if="aisle && aisle.direction === 'horizontal' && aisle.position > 0 && aisle.position === rowIndex + 1" class="thumbnail-horizontal-aisle-row">
                    <template v-for="(seat, colIndex) in row" :key="`h-aisle-seat-${colIndex}`">
                      <div class="thumbnail-horizontal-aisle"></div>
                      <template v-for="vAisle in layoutConfig.aisles" :key="`h-aisle-v-${rowIndex}-${vAisle?.aisleNumber || rowIndex}`">
                        <div v-if="vAisle && vAisle.direction === 'vertical' && vAisle.position > 0 && vAisle.position === colIndex + 1" class="thumbnail-aisle-thumbnail-intersection"></div>
                      </template>
                    </template>
                  </div>
                </template>
              </template>
            </div>
          </div>
        </div>
        
        <div class="layout-preview" id="layout-preview" :class="{ maximized: isMaximized }" :style="isMaximized ? { position: 'fixed', inset: '0', zIndex: 3000, background: '#fff' } : {}">
          <div class="layout-preview-header">
            <h3>布局图</h3>
            <div class="layout-preview-actions">
              <el-button type="primary" @click="saveLayout">保存布局</el-button>
              <el-button type="default" @click="toggleMaximize">{{ isMaximized ? '还原' : '最大化' }}</el-button>
            </div>
          </div>
          <div id="screen-indicator" class="screen-indicator" :class="layoutConfig.podiumStyle">主席台</div>
          <div class="layout-scroll-container" id="layout-scroll-container">
            <div id="seat-layout-container" class="seat-layout-container">
              <div class="seat-grid">
                <div class="seat-row-labels">
                  <div class="row-label-header">排</div>
                  <template v-for="(row, rowIndex) in seatLayout" :key="rowIndex">
                    <div class="row-label">{{ rowIndex + 1 }}</div>
                    <template v-for="(aisle, aisleIdx) in layoutConfig.aisles" :key="`h-aisle-label-${rowIndex}-${aisle?.aisleNumber || aisleIdx}`">
                      <div v-if="aisle && aisle.direction === 'horizontal' && aisle.position > 0 && aisle.position === rowIndex + 1" class="row-label-placeholder"></div>
                    </template>
                  </template>
                </div>
                <div class="seat-grid-content">
                  <div class="row-label-header-spacer"></div>
                  <template v-for="(row, rowIndex) in seatLayout" :key="rowIndex">
                    <div class="seat-row">
                      <template v-for="(seat, colIndex) in row" :key="colIndex">
                        <div class="seat" :class="{ available: seat.available, unavailable: !seat.available }" @click="toggleSeat(rowIndex, colIndex)" @dblclick="editSeatNumber(rowIndex, colIndex)" title="双击编辑座位号">
                          <span class="seat-number">{{ seat.seat_number }}</span>
                        </div>
                        <template v-for="aisle in layoutConfig.aisles" :key="`aisle-${rowIndex}-${aisle?.aisleNumber || rowIndex}`">
                          <div v-if="aisle && aisle.direction === 'vertical' && aisle.position > 0 && aisle.position === colIndex + 1" class="aisle vertical-aisle"></div>
                        </template>
                      </template>
                    </div>
                    <template v-for="(aisle, aisleIdx) in layoutConfig.aisles" :key="`h-aisle-${rowIndex}-${aisle?.aisleNumber || aisleIdx}`">
                      <div v-if="aisle && aisle.direction === 'horizontal' && aisle.position > 0 && aisle.position === rowIndex + 1" class="horizontal-aisle-row">
                        <template v-for="(seat, colIndex) in row" :key="`h-aisle-seat-${colIndex}`">
                          <div class="horizontal-aisle"></div>
                          <template v-for="vAisle in layoutConfig.aisles" :key="`h-aisle-v-${rowIndex}-${vAisle?.aisleNumber || rowIndex}`">
                            <div v-if="vAisle && vAisle.direction === 'vertical' && vAisle.position > 0 && vAisle.position === colIndex + 1" class="aisle horizontal-aisle-intersection"></div>
                          </template>
                        </template>
                      </div>
                    </template>
                  </template>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <template v-if="!isMaximized" #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="saveLayout">保存布局</el-button>
          <el-button @click="cancelLayout">取 消</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="ConferenceRoom">
import {
  listConferenceRoom,
  getConferenceRoom,
  addConferenceRoom,
  updateConferenceRoom,
  delConferenceRoom,
  exportConferenceRoom,
  changeConferenceRoomStatus,
  getConferenceRoomLayoutByRoomId,
  saveConferenceRoomLayout
} from "@/api/system/conferenceRoom";

import { ref, reactive, toRefs, onMounted, getCurrentInstance } from 'vue';

const { proxy } = getCurrentInstance();
const { sys_normal_disable } = proxy.useDict("sys_normal_disable");

const conferenceRoomList = ref([]);
const open = ref(false);
const loading = ref(true);
const showSearch = ref(true);
const ids = ref([]);
const single = ref(true);
const multiple = ref(true);
const total = ref(0);
const title = ref("");
const dateRange = ref([]);

// 布局设置相关
const layoutOpen = ref(false);
const layoutTitle = ref("");
const layoutRoomId = ref(undefined);
const isMaximized = ref(false);
const layoutConfig = ref({
  podiumStyle: 'bar',
  rows: 5,
  columns: 6,
  seatNumberType: 'odd-even',
  aisleCount: 0,
  aisles: [],
  showThumbnail: false
});
const seatLayout = ref([]);

// 列显隐信息
const columns = ref({
  roomId: { label: "会议室编号", visible: false },
  roomName: { label: "会议室名称", visible: true },
  capacity: { label: "容纳人数", visible: true },
  location: { label: "位置", visible: true },
  equipment: { label: "会议设备", visible: true },
  tags: { label: "标签", visible: true },
  status: { label: "状态", visible: true },
  createTime: { label: "创建时间", visible: true },
});

const data = reactive({
  form: {},
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    roomName: undefined,
    location: undefined,
    status: undefined,
  },
  rules: {
    roomName: [
      { required: true, message: "会议室名称不能为空", trigger: "blur" },
      { min: 1, max: 50, message: "会议室名称长度必须介于 1 和 50 之间", trigger: "blur" },
    ],
    capacity: [
      { required: true, message: "容纳人数不能为空", trigger: "blur" },
      { type: "number", min: 1, message: "容纳人数必须大于 0", trigger: "blur" },
    ],
    location: [
      { required: true, message: "位置不能为空", trigger: "blur" },
      { min: 1, max: 100, message: "位置长度必须介于 1 和 100 之间", trigger: "blur" },
    ],
    equipment: [
      { max: 200, message: "会议设备长度不能超过 200 个字符", trigger: "blur" },
    ],
  },
});

const { queryParams, form, rules } = toRefs(data);

/** 查询会议室列表 */
function getList() {
  loading.value = true;
  listConferenceRoom(proxy.addDateRange(queryParams.value, dateRange.value)).then(
    (res) => {
      loading.value = false;
      conferenceRoomList.value = res.rows;
      total.value = res.total;
    }
  );
}

/** 搜索按钮操作 */
function handleQuery() {
  queryParams.value.pageNum = 1;
  getList();
}

/** 重置按钮操作 */
function resetQuery() {
  dateRange.value = [];
  proxy.resetForm("queryRef");
  handleQuery();
}

/** 删除按钮操作 */
function handleDelete(row) {
  const roomIds = row.roomId || ids.value;
  proxy.$modal
    .confirm('是否确认删除会议室编号为"' + roomIds + '"的数据项？')
    .then(function () {
      return delConferenceRoom(roomIds);
    })
    .then(() => {
      getList();
      proxy.$modal.msgSuccess("删除成功");
    })
    .catch(() => {});
}

/** 导出按钮操作 */
function handleExport() {
  proxy.download(
    "system/conferenceRoom/export",
    {
      ...queryParams.value,
    },
    `conferenceRoom_${new Date().getTime()}.xlsx`
  );
}

/** 会议室状态修改  */
function handleStatusChange(row) {
  let text = row.status === "0" ? "启用" : "停用";
  proxy.$modal
    .confirm('确认要"' + text + '""' + row.roomName + '"会议室吗?')
    .then(function () {
      return changeConferenceRoomStatus(row.roomId, row.status);
    })
    .then(() => {
      proxy.$modal.msgSuccess(text + "成功");
    })
    .catch(function () {
      row.status = row.status === "0" ? "1" : "0";
    });
}

/** 选择条数  */
function handleSelectionChange(selection) {
  ids.value = selection.map((item) => item.roomId);
  single.value = selection.length != 1;
  multiple.value = !selection.length;
}

/** 重置操作表单 */
function reset() {
  form.value = {
    roomId: undefined,
    roomName: undefined,
    capacity: undefined,
    location: undefined,
    equipment: undefined,
    tags: undefined,
    status: "0",
    remark: undefined,
  };
  proxy.resetForm("conferenceRoomRef");
}

/** 取消按钮 */
function cancel() {
  open.value = false;
  reset();
}

/** 新增按钮操作 */
function handleAdd() {
  reset();
  open.value = true;
  title.value = "添加会议室";
}

/** 修改按钮操作 */
function handleUpdate(row) {
  reset();
  const roomId = row.roomId || ids.value;
  getConferenceRoom(roomId).then((response) => {
    form.value = response.data.data;
    open.value = true;
    title.value = "修改会议室";
  });
}

/** 提交按钮 */
function submitForm() {
  proxy.$refs["conferenceRoomRef"].validate((valid) => {
    if (valid) {
      if (form.value.roomId != undefined) {
        updateConferenceRoom(form.value).then((response) => {
          proxy.$modal.msgSuccess("修改成功");
          open.value = false;
          getList();
        });
      } else {
        addConferenceRoom(form.value).then((response) => {
          proxy.$modal.msgSuccess("新增成功");
          open.value = false;
          getList();
        });
      }
    }
  });
}

/** 打开布局设置对话框 */
function handleLayout(row) {
  layoutRoomId.value = row.roomId;
  layoutTitle.value = `设置${row.roomName}的布局`;
  isMaximized.value = false;
  // 初始化布局配置
  initializeLayout();
  // 加载已有布局（如果存在），完成后打开对话框
  loadLayout(row.roomId).finally(() => {
    layoutOpen.value = true;
  });
}

/** 初始化布局 */
function initializeLayout() {
  // 重置布局配置
  layoutConfig.value = {
    podiumStyle: 'bar',
    rows: 5,
    columns: 6,
    seatNumberType: 'odd-even',
    aisleCount: 0,
    aisles: [],
    showThumbnail: false
  };
  // 生成座位布局（含座位号计算）
  generateSeatLayout();
}

/** 生成座位布局（含座位号计算） */
function generateSeatLayout() {
  const rows = layoutConfig.value.rows;
  const cols = layoutConfig.value.columns;
  const type = layoutConfig.value.seatNumberType;
  const layout = [];

  const mid = Math.floor(cols / 2);

  for (let i = 0; i < rows; i++) {
    const row = [];
    for (let j = 0; j < cols; j++) {
      row.push({
        seat_number: j + 1,
        available: true
      });
    }

    // 计算该行的座位号编排
    if (type === 'odd-even') {
      let oddNumber = cols % 2 === 0 ? 2 * mid - 1 : 2 * mid + 1;
      for (let j = 0; j < mid; j++) {
        row[j].seat_number = oddNumber;
        oddNumber -= 2;
      }
      if (cols % 2 === 1) {
        row[mid].seat_number = 1;
      }
      let evenNumber = 2;
      for (let j = cols % 2 === 1 ? mid + 1 : mid; j < cols; j++) {
        row[j].seat_number = evenNumber;
        evenNumber += 2;
      }
    } else if (type === 'even-odd') {
      let evenNumber = 2 * mid;
      for (let j = 0; j < mid; j++) {
        row[j].seat_number = evenNumber;
        evenNumber -= 2;
      }
      let oddNumber = 1;
      for (let j = mid; j < cols; j++) {
        row[j].seat_number = oddNumber;
        oddNumber += 2;
      }
    } else if (type === 'sequential') {
      for (let j = 0; j < cols; j++) {
        row[j].seat_number = j + 1;
      }
    } else if (type === 'reverse') {
      for (let j = cols - 1; j >= 0; j--) {
        row[j].seat_number = cols - j;
      }
    }

    layout.push(row);
  }

  seatLayout.value = layout;
}

/** 更新布局 */
function updateLayout() {
  // 更新通道配置
  const aisleCount = layoutConfig.value.aisleCount;
  const currentAisles = layoutConfig.value.aisles;
  
  if (aisleCount > currentAisles.length) {
    // 添加新通道
    for (let i = currentAisles.length; i < aisleCount; i++) {
      currentAisles.push({
        aisleNumber: i + 1,
        direction: 'vertical',
        position: 'auto'
      });
    }
  } else if (aisleCount < currentAisles.length) {
    // 移除多余通道
    currentAisles.splice(aisleCount);
  }
  
  // 重新生成座位布局
  generateSeatLayout();
}

/** 更新座位布局编排（用于座位号类型变更） */
function updateSeatLayout() {
  generateSeatLayout();
}

/** 切换座位状态 */
function toggleSeat(rowIndex, colIndex) {
  seatLayout.value[rowIndex][colIndex].available = !seatLayout.value[rowIndex][colIndex].available;
}

/** 编辑座位号 */
function editSeatNumber(rowIndex, colIndex) {
  const newNumber = prompt('请输入新的座位号:', seatLayout.value[rowIndex][colIndex].seat_number);
  if (newNumber && !isNaN(newNumber)) {
    seatLayout.value[rowIndex][colIndex].seat_number = parseInt(newNumber);
  }
}

/** 获取通道位置标签 */
function getAislePositionLabel(pos) {
  if (seatLayout.value.length > 0) {
    const firstRow = seatLayout.value[0];
    const leftIdx = pos - 1;
    const rightIdx = pos;
    if (leftIdx >= 0 && rightIdx < firstRow.length) {
      const seatNumber1 = firstRow[leftIdx].seat_number;
      const seatNumber2 = firstRow[rightIdx].seat_number;
      return `${seatNumber1}和${seatNumber2}之间`;
    }
  }
  return `${pos}和${pos + 1}之间`;
}

/** 保存布局 */
async function saveLayout() {
  // 构建布局数据
  const layoutData = {
    roomId: layoutRoomId.value,
    config: layoutConfig.value,
    seats: seatLayout.value
  };
  
  try {
    // 调用后端 API 保存布局
    const response = await saveConferenceRoomLayout(layoutData);
    if (response.code === 200) {
      proxy.$modal.msgSuccess('布局保存成功');
      layoutOpen.value = false;
    } else {
      proxy.$modal.msgError('布局保存失败');
    }
  } catch (error) {
    console.error('保存布局失败:', error);
    proxy.$modal.msgError('布局保存失败');
  }
}

/** 取消布局设置 */
function cancelLayout() {
  layoutOpen.value = false;
}

/** 切换最大化状态 */
function toggleMaximize() {
  isMaximized.value = !isMaximized.value;
}

/** 切换缩略图显示 */
function toggleThumbnail() {
  // 缩略图显示逻辑已在模板中通过 v-if 实现
}

/** 加载已有布局 */
async function loadLayout(roomId) {
  try {
    // 调用后端 API 加载布局
    const response = await getConferenceRoomLayoutByRoomId(roomId);
    if (response.code === 200 && response.data) {
      const layoutData = response.data;
      if (layoutData.config) {
        layoutConfig.value = { ...layoutConfig.value, ...layoutData.config };
      }
      if (layoutData.seats) {
        seatLayout.value = layoutData.seats;
      }
    }
  } catch (error) {
    console.error('加载布局失败:', error);
    // 加载失败时使用默认布局
    initializeLayout();
  }
}

onMounted(() => {
  getList();
});
</script>

<style scoped>
/* 布局编辑器样式 */
.layout-editor {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.layout-config {
  background-color: #f5f7fa;
  padding: 20px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.layout-config h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.config-form-row {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 150px;
}

.form-group > .aisle-position-item {
  margin-top: 0;
}

.form-group label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.aisle-position-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  flex-wrap: nowrap;
  width: 100%;
}

.aisle-position-item label {
  font-size: 14px;
  color: #606266;
  white-space: nowrap;
  flex-shrink: 0;
}

.aisle-position-item .el-select {
  min-width: 120px;
  flex-shrink: 0;
}

.config-actions-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
}

.layout-legend {
  display: flex;
  gap: 20px;
}

.layout-legend p {
  display: flex;
  align-items: center;
  gap: 5px;
  margin: 0;
  font-size: 14px;
  color: #606266;
}

.seat-legend {
  width: 16px;
  height: 16px;
  border-radius: 2px;
  display: inline-block;
}

.seat-legend.available {
  background-color: #67c23a;
}

.seat-legend.unavailable {
  background-color: #f56c6c;
}

.seat-legend.screen {
  background-color: #409eff;
}

.show-thumbnail-option {
  font-size: 14px;
}

.layout-thumbnail-section {
  background-color: #f5f7fa;
  padding: 20px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  text-align: center;
}

.layout-thumbnail-section h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.thumbnail-container {
  width: 100%;
  overflow: auto;
  display: flex;
  justify-content: center;
}

.thumbnail-grid {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.thumbnail-row {
  display: flex;
  gap: 2px;
}

.thumbnail-seat {
  width: 10px;
  height: 10px;
  border-radius: 1px;
}

.thumbnail-seat.available {
  background-color: #67c23a;
}

.thumbnail-seat.unavailable {
  background-color: #f56c6c;
}

.thumbnail-aisle {
  width: 8px;
  height: 10px;
  background-color: #e4e7ed;
}

.thumbnail-horizontal-aisle-row {
  display: flex;
  gap: 2px;
}

.thumbnail-horizontal-aisle {
  width: 10px;
  height: 10px;
  background-color: #e4e7ed;
  border-radius: 1px;
}

.thumbnail-aisle-thumbnail-intersection {
  width: 8px;
  height: 10px;
  background-color: #d0d4db;
}

.layout-preview {
  background-color: #f5f7fa;
  padding: 20px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  position: relative;
}

.layout-preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.layout-preview-header h3 {
  margin: 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.layout-preview-actions {
  display: flex;
  gap: 10px;
}

.screen-indicator {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #409eff;
  color: white;
  padding: 5px 20px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  z-index: 10;
}

.screen-indicator.bar {
  width: 200px;
  text-align: center;
}

.screen-indicator.round {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.layout-scroll-container {
  margin-top: 80px;
  overflow: auto;
  max-height: 500px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background-color: white;
  padding: 20px;
}

.layout-scroll-container::-webkit-scrollbar {
  width: 12px;
  height: 12px;
}

.layout-scroll-container::-webkit-scrollbar-thumb {
  background-color: #c0c4cc;
  border-radius: 6px;
}

.layout-scroll-container::-webkit-scrollbar-thumb:hover {
  background-color: #909399;
}

.layout-scroll-container::-webkit-scrollbar-track {
  background-color: #f5f7fa;
  border-radius: 6px;
}

.seat-layout-container {
  min-width: fit-content;
  display: flex;
  justify-content: center;
}

.seat-grid {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.seat-row-labels {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: center;
}

/* 确保排数数字与座位行对齐 */
.seat-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.row-label-placeholder {
  width: 40px;
  height: 40px;
  border-radius: 4px;
}

.row-label-header {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: #606266;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-weight: 600;
}

.row-label-header-spacer {
  width: 100%;
  height: 40px;
}

.seat-grid-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.row-label {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: #606266;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.seat-row {
  display: flex;
  gap: 10px;
}

.seat {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.seat.available {
  background-color: #67c23a;
  color: white;
}

.seat.available:hover {
  background-color: #85ce61;
  transform: scale(1.1);
}

.seat.unavailable {
  background-color: #f56c6c;
  color: white;
}

.seat.unavailable:hover {
  background-color: #f78989;
  transform: scale(1.1);
}

.seat-number {
  font-size: 12px;
}

.aisle {
  width: 40px;
  height: 40px;
  background-color: #e4e7ed;
  border-radius: 4px;
}

.horizontal-aisle-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.horizontal-aisle {
  width: 40px;
  height: 40px;
  background-color: #e4e7ed;
  border-radius: 4px;
}

.horizontal-aisle-intersection {
  background-color: #d0d4db;
  border-radius: 4px;
}

/* 响应式调整 */
@media (max-width: 1200px) {
  .config-form-row {
    flex-direction: column;
  }
  
  .form-group {
    width: 100%;
  }
  
  .aisle-position-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
}

/* 对话框最大化 */
:deep(.el-dialog__wrapper.layout-dialog-maximized) {
  padding: 0;
  margin: 0;
}

:deep(.el-dialog__wrapper.layout-dialog-maximized .el-dialog) {
  width: 100% !important;
  max-width: 100% !important;
  height: 100vh;
  margin: 0;
  border-radius: 0;
}

:deep(.el-dialog__wrapper.layout-dialog-maximized .el-dialog__header) {
  display: none;
}

:deep(.el-dialog__wrapper.layout-dialog-maximized .el-dialog__body) {
  padding: 0;
  margin: 0;
}

:deep(.el-dialog__wrapper.layout-dialog-maximized) .layout-editor {
  height: 100%;
  flex: 1;
}

/* 对话框默认样式 */
:deep(.el-dialog__body) {
  padding: 20px;
}

:deep(.el-dialog__header) {
  padding: 20px 20px 10px;
}

:deep(.el-dialog__footer) {
  padding: 10px 20px 20px;
}

/* 最大化时布局图铺满全屏 */
.layout-preview.maximized {
  padding: 10px;
}

.layout-preview.maximized .layout-scroll-container {
  max-height: calc(100vh - 80px);
  border: none;
  background-color: #f5f7fa;
  margin-top: 10px;
}
</style>
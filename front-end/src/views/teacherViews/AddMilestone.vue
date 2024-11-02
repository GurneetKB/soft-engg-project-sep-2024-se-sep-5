<script setup>
import { ref, onMounted } from 'vue'

const count = ref(0)

function increment() {
  count.value++
}

onMounted(() => {
  console.log(`The initial count is ${count.value}.`)
})

const tasks = ref([''])

function addTask() {
  tasks.value.push('')
}
</script>

<template>
  <div class="page-wrapper">
    <div class="container my-5">
      <div class="card shadow-lg p-4 mx-auto">
        <h2 class="mb-4 text-center gradient-text">Create New Milestone</h2>

        <div class="mb-4">
          <label for="titleInput" class="form-label fw-bold">Title</label>
          <input
            type="text"
            class="form-control form-control-lg custom-input"
            id="titleInput"
            placeholder="Enter milestone title"
          />
        </div>

        <div class="mb-4">
          <label for="descriptionArea" class="form-label fw-bold"
            >Description</label
          >
          <textarea
            class="form-control custom-input"
            id="descriptionArea"
            rows="4"
            placeholder="Enter milestone description"
          ></textarea>
        </div>

        <div class="task-list mb-4">
          <label for="tasksInput" class="form-label fw-bold">Tasks</label>
          <div
            v-for="(task, index) in tasks"
            :key="index"
            class="task-item mb-3"
          >
            <input
              type="text"
              class="form-control custom-input"
              :placeholder="'Enter task ' + (index + 1)"
              v-model="tasks[index]"
            />
          </div>
          <div class="text-center mt-3">
            <button
              @click="addTask"
              type="button"
              class="btn btn-outline-primary rounded-circle add-btn"
            >
              <i class="bi bi-plus-lg"></i>
            </button>
          </div>
        </div>

        <div class="text-center">
          <button class="btn btn-gradient btn-lg px-5">
            <i class="bi bi-check2-circle me-2"></i>
            Publish Milestone
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.task-item {
  position: relative;
}

.add-btn {
  width: 40px;
  height: 40px;
  padding: 0;
  /* display: flex; */
  align-items: center;
  justify-content: center;
  transition: transform 0.2s ease;
}

.add-btn:hover {
  transform: scale(1.1);
}

.page-wrapper {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f2 100%);
  padding: 20px;
}

.container {
  max-width: 800px;
}

.card {
  border-radius: 20px;
  border: none;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  max-width: 700px;
}

.gradient-text {
  background: linear-gradient(45deg, #1a5f7a, #159957);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  font-weight: 600;
}

.custom-input {
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  padding: 12px;
  transition: all 0.3s ease;
}

.custom-input:focus {
  border-color: #159957;
  box-shadow: 0 0 0 0.2rem rgba(21, 153, 87, 0.15);
  transform: translateY(-1px);
}

.btn-gradient {
  background: linear-gradient(45deg, #159957, #155799);
  border: none;
  color: white;
  transition: all 0.3s ease;
  font-weight: 500;
  letter-spacing: 0.5px;
  border-radius: 10px;
}

.btn-gradient:hover {
  background: linear-gradient(45deg, #138346, #124e85);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.form-label {
  color: #2c3e50;
  margin-bottom: 8px;
  font-size: 1.1rem;
}

/* Additional hover effects */
.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

input::placeholder,
textarea::placeholder {
  color: #999;
  font-size: 0.95rem;
}
</style>

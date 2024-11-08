<template>
  <router-view v-if="$route.name !== 'MilestoneManagement'"></router-view>
  <div v-else>
    <section class="py-5">
      <div class="container px-4">
        <div class="row g-4 justify-content-center mx-0">
          <div class="col-sm-5 px-2">
            <div class="stats-card rounded-lg shadow-sm">
              <div class="card-body d-flex flex-column align-items-center">
                <h2 class="card-title fw-bold mb-4 text-dark">
                  Total Registered Students
                </h2>
                <div class="stats-number text-primary">234</div>
              </div>
            </div>
          </div>
          <div class="col-sm-5 px-2">
            <div class="stats-card rounded-lg shadow-sm">
              <div class="card-body d-flex flex-column align-items-center">
                <h2 class="card-title fw-bold mb-4 text-dark">
                  Total Number of Teams
                </h2>
                <div class="stats-number text-primary">50</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="py-5 bg-light">
      <div class="container hero-section py-5 rounded-lg px-4 shadow-sm">
        <div class="text-center mb-4 position-relative">
          <h2 class="main-title text-dark">Milestones</h2>
          <button
            class="btn btn-success rounded-circle add-button position-absolute"
            style="right: 20px; top: 0"
          >
            <RouterLink
              class="nav-link"
              to="/teacher/milestone_management/add_milestone"
            >
              <i class="bi bi-plus fs-0" style="font-size: 4rem"></i>
            </RouterLink>
          </button>
        </div>
        <div class="milestone-wrapper">
          <div
            v-for="milestone in milestonesWithStatus"
            :key="milestone.name"
            class="milestone-item mb-4"
          >
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="milestone-title mb-0">{{ milestone.title }}</h5>
              <div class="d-flex gap-2">
                <RouterLink
                  class="btn btn-outline-primary btn-sm"
                  :to="
                    '/teacher/milestone_management/edit_milestone/' +
                    milestone.id
                  "
                >
                  <i class="bi bi-pencil-square"></i>
                </RouterLink>
                <button
                  class="btn btn-outline-danger btn-sm"
                  @click="deleteMilestone(milestone.id)"
                >
                  <i class="bi bi-trash"></i>
                </button>
              </div>
            </div>
            <div class="progress">
              <div
                :class="'progress-bar progress-bar-' + milestone.status"
                role="progressbar"
                :style="{ width: milestone.progress + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.add-button {
  width: 70px;
  height: 70px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.hero-section {
  background: #ffffff;
  border-radius: 20px;
}

.stats-card {
  background: #ffffff;
  padding: 2rem;
  border: 1px solid #ddd;
  border-radius: 15px;
  transition: all 0.3s ease;
}

.main-title {
  font-size: 2rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: #333;
}

.stats-number {
  font-size: 2.5rem;
  font-weight: bold;
  padding: 1rem 2rem;
  background: rgba(0, 123, 255, 0.1);
  color: #007bff;
  border-radius: 10px;
}

.milestone-wrapper {
  max-width: 700px;
  margin: 0 auto;
  padding: 0 20px;
}

.milestone-item {
  background: rgba(0, 0, 0, 0.03);
  padding: 20px;
  border-radius: 10px;
}

.milestone-title {
  font-weight: 600;
  margin-bottom: 10px;
  color: #333;
}

.progress {
  height: 1rem;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 5px;
}

.progress-bar-success {
  background-color: #a8d5ba;
  /* Pastel green */
}

.progress-bar-warning {
  background-color: #ffd966;
  /* Pastel yellow */
}

.progress-bar-danger {
  background-color: #ffb3b3;
  /* Pastel red */
}

.card-title {
  font-size: 1.2rem;
  text-align: center;
  color: #333;
}
</style>

<script>
import { fetchfunct } from '@/components/fetch'
export default {
  data() {
    return {
      milestones: [],
    }
  },
  computed: {
    milestonesWithStatus() {
      return this.milestones.map(milestone => {
        let status = 'light'
        if (milestone.progress === 100) {
          status = 'success'
        } else if (milestone.progress > 50) {
          status = 'warning'
        } else if (milestone.progress > 0 && milestone.progress <= 50) {
          status = 'danger'
        }
        return { ...milestone, status }
      })
    },
  },
  methods: {
    async getAllMilestones() {
      const res = await fetchfunct('api/instructor/all_milestone')
      const data = await res.json().catch(e => {})

      if (res.ok) {
        this.milestones = data

        console.log(this.milestones)
      } else {
        this.error = res.status
      }
    },
    async deleteMilestone(milestone_id) {
      if (confirm('Do you really want to delete?')) {
        const res = await fetchfunct(
          `api/instructor/milestone/${milestone_id}`,
          {
            method: 'DELETE',
          },
        )
        const data = await res.json().catch(e => {})

        if (res.ok) {
          this.$router.go(0)
        } else {
          this.error = res.status
        }
      }
    },
  },
  mounted() {
    this.getAllMilestones()
  },
}
</script>

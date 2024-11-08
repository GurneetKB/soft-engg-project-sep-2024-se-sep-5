<script>
  import { fetchfunct } from '@/components/fetch';
  export default {
    props: [ 'id' ],
    data ()
    {
      return {
        milestone_data: {
          title: '',
          description: '',
          deadline: '',
          tasks: [],
        },
      }
    },
    mounted ()
    {
      if ( this.id )
      {
        this.fetchMilestoneDetails( this.id )
      } else
      {
        console.error( 'Milestone ID is undefined' )
      }
    },
    methods: {
      async fetchMilestoneDetails ( id )
      {
        try
        {
          const res = await fetchfunct(
            `api/instructor/milestone/${ id }`,
          )
          const data = await res.json()
          if ( res.ok )
          {
            this.milestone_data = data
          } else
          {
            console.error( 'Failed to fetch milestone details:', res.status )
          }
        } catch ( error )
        {
          console.error( 'Error fetching milestone:', error )
        }
      },
      async updateMilestone ()
      {
        try
        {
          const { title, description, deadline, tasks } = this.milestone_data
          const res = await fetchfunct(
            `api/instructor/milestone/${ this.id }`,
            {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify( { title, description, deadline, tasks } ),
            },
          )
          if ( res.ok )
          {
            this.$router.push( { name: 'milestone_list' } )
          } else
          {
            console.error( 'Failed to update milestone' )
          }
        } catch ( error )
        {
          console.error( 'Error updating milestone:', error )
        }
      },
      addTask ()
      {
        if ( !this.milestone_data.tasks )
        {
          this.milestone_data.tasks = []
        }
        this.milestone_data.tasks.push( { text: '' } )
      },
      removeTask ( index )
      {
        this.milestone_data.tasks.splice( index, 1 )
      },
    },
  }
</script>

<template>
  <div class="page-wrapper">
    <div class="container my-5">
      <div class="card shadow-lg p-4 mx-auto">
        <button @click="$router.back()" class="me-auto p-2 btn btn-link text-decoration-none">
          ← Back
        </button>
        <h2 class="mb-4 text-center gradient-text">Edit Milestone</h2>

        <div class="mb-4">
          <label for="titleInput" class="form-label fw-bold">Title</label>
          <input type="text" class="form-control form-control-lg custom-input" id="titleInput"
            v-model="milestone_data.title" />
        </div>

        <div class="mb-4">
          <label for="descriptionArea" class="form-label fw-bold">Description</label>
          <textarea class="form-control custom-input" id="descriptionArea" rows="4"
            v-model="milestone_data.description"></textarea>
        </div>

        <div class="mb-4">
          <label for="deadlineInput" class="form-label fw-bold">Deadline</label>
          <input type="datetime-local" class="form-control form-control-lg custom-input" id="deadlineInput"
            v-model="milestone_data.deadline" :min="new Date().toISOString().slice(0, 16)" />
        </div>

        <div class="task-list mb-4">
          <label for="tasksInput" class="form-label fw-bold">Tasks</label>
          <div v-for="(task, index) in milestone_data.tasks" :key="index" class="mb-4 d-flex align-items-center">
            <input type="text" class="form-control custom-input me-2" :placeholder="'Enter task ' + (index + 1)"
              v-model="task.text" />
            <button @click="removeTask(index)" type="button" class="btn btn-outline-danger rounded-circle delete-btn"
              style="width: 25px; height: 23px; padding: 0">
              <i class="bi bi-dash-lg"></i>
            </button>
          </div>
          <div class="text-center mt-3">
            <button @click="addTask" type="button" class="btn btn-outline-primary rounded-circle add-btn">
              <i class="bi bi-plus-lg"></i>
            </button>
          </div>
        </div>

        <div class="text-center">
          <button class="btn btn-gradient btn-lg px-5" @click="updateMilestone()"
            style="font-family: 'Segoe UI', Arial, sans-serif">
            <i class="bi bi-arrow-clockwise me-2"></i>
            Update Milestone
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
    align-items: center;
    justify-content: center;
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
    background: #1a5f7a;
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    font-weight: 600;
  }

  .custom-input {
    border: 2px solid #e0e0e0;
    border-radius: 10px;
    padding: 12px;
  }

  .custom-input:focus {
    border-color: #159957;
    box-shadow: 0 0 0 0.2rem rgba(21, 153, 87, 0.15);
    transform: translateY(-1px);
  }

  .btn-gradient {
    background: #159957;
    border: none;
    color: white;
    font-weight: 500;
    letter-spacing: 0.5px;
    border-radius: 10px;
  }

  .btn-gradient:hover {
    background: #138346;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  }

  .form-label {
    color: #2c3e50;
    margin-bottom: 8px;
    font-size: 1.1rem;
  }

  input::placeholder,
  textarea::placeholder {
    color: #999;
    font-size: 0.95rem;
  }
</style>

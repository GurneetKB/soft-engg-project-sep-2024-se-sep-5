<script setup>
  import { ref, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { checkerror, checksuccess, fetchfunct } from '@/components/fetch'
  import LoadingPlaceholder from '@/components/LoadingPlaceholder.vue'
  import { Form, Field, ErrorMessage, FieldArray } from 'vee-validate'
  import * as Yup from 'yup'
  import { localDateInISOFormat } from '@/components/date'

  const props = defineProps( {
    id: {
      type: String,
      required: true
    }
  } )

  const router = useRouter()

  const initialValues = ref( {
    title: '',
    description: '',
    deadline: '',
    tasks: [ { description: '' } ]
  } )

  const validationSchema = Yup.object( {
    title: Yup.string().required( 'Milestone title is required' ),
    description: Yup.string().required( 'Milestone description is required' ),
    deadline: Yup.date()
      .min( new Date(), 'Deadline must be in the future' )
      .required( 'Deadline is required' ),
    tasks: Yup.array().of(
      Yup.object().shape( {
        description: Yup.string().required( 'Task description is required' )
      } )
    ).min( 1, 'At least one task is required' )
  } )

  const loading = ref( false )
  const loadingOnMount = ref( true )
  const formRef = ref( null )

  const handleUpdateButtonClick = ( values ) =>
  {
    new bootstrap.Modal( '#updateConfirmation' ).show()
  }

  const updateMilestone = async () =>
  {
    bootstrap.Modal.getInstance( document.getElementById( 'updateConfirmation' ) ).hide()
    const formValues = { ...formRef.value.values };
    if ( !formValues ) return
    loading.value = true
    formValues.deadline = new Date( formValues.deadline ).toUTCString()
    const res = await fetchfunct( `teacher/milestone_management/${ props.id }`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify( formValues ),
    } )
    if ( res.ok )
    {
      router.push( "/teacher/milestone_management" )
      checksuccess( res )
    } else
    {
      checkerror( res )
    }

    loading.value = false
  }

  onMounted( async () =>
  {
    loadingOnMount.value = true
    const res = await fetchfunct( `teacher/milestone_management/${ props.id }` )
    if ( res.ok )
    {
      const data = await res.json()
      initialValues.value = {
        title: data.title || '',
        description: data.description || '',
        deadline: localDateInISOFormat( new Date( data.deadline ) ) || '',
        tasks: data.tasks && data.tasks.length > 0
          ? data.tasks.map( task => ( { description: task.description || '' } ) )
          : [ { description: '' } ]
      }
    } else
    {
      checkerror( res )
    }

    loadingOnMount.value = false
  }
  )
</script>

<template>
  <div class="page-wrapper">
    <div class="container my-5">
      <div class="card shadow-lg p-4 mx-auto">
        <button @click="router.back()" class="me-auto p-2 btn btn-link text-decoration-none">
          ← Back
        </button>
        <h2 class="mb-4 text-center gradient-text">Edit Milestone</h2>
        <LoadingPlaceholder v-if="loadingOnMount" variant="form" :count="1" />
        <Form v-else :validation-schema="validationSchema" :initial-values="initialValues" ref="formRef"
          @submit="handleUpdateButtonClick">
          <div class="mb-4">
            <label for="titleInput" class="form-label fw-bold">Title</label>
            <Field name="title" type="text" id="titleInput" class="form-control form-control-lg custom-input"
              placeholder="Enter milestone title" />
            <ErrorMessage name="title" class="form-text" />
          </div>

          <div class="mb-4">
            <label for="descriptionArea" class="form-label fw-bold">Description</label>
            <Field name="description" as="textarea" id="descriptionArea" class="form-control custom-input" rows="4"
              placeholder="Enter milestone description" />
            <ErrorMessage name="description" class="form-text" />
          </div>

          <div class="mb-4">
            <label for="deadlineInput" class="form-label fw-bold">Deadline</label>
            <Field name="deadline" type="datetime-local" id="deadlineInput"
              class="form-control form-control-lg custom-input" :min="new Date().toISOString().slice(0, 16)" />
            <ErrorMessage name="deadline" class="form-text" />
          </div>

          <div class="task-list mb-4">
            <label class="form-label fw-bold">Tasks</label>
            <FieldArray name="tasks" v-slot="{ fields, push, remove }">
              <div v-for="(field, index) in fields" :key="field.key" class="task-item mb-3">
                <div class="d-flex align-items-center">
                  <Field :name="`tasks[${index}].description`" type="text" class="form-control custom-input me-2"
                    :placeholder="`Enter task ${index + 1}`" />
                  <button v-if="fields.length > 1" @click="remove(index)" type="button"
                    class="btn btn-outline-danger rounded-circle delete-btn"
                    style="width: 25px; height: 23px; padding: 0">
                    <i class="bi bi-dash-lg"></i>
                  </button>
                </div>
                <ErrorMessage :name="`tasks[${index}].description`" class="form-text" />
              </div>
              <div class="text-center mt-3">
                <button @click="push({ description: '' })" type="button"
                  class="btn btn-outline-primary rounded-circle add-btn">
                  <i class="bi bi-plus-lg"></i>
                </button>
              </div>
            </FieldArray>
            <ErrorMessage name="tasks" class="form-text" />
          </div>

          <div class="text-center">
            <button type="submit" class="btn btn-gradient btn-lg px-5" :disabled="loading">
              <span v-if="!loading">
                <i class="bi bi-arrow-clockwise me-2"></i>Update Milestone
              </span>
              <span v-else>
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                <span class="align-middle"> Loading...</span>
              </span>
            </button>
          </div>
        </Form>
      </div>
    </div>
  </div>

  <div class="modal" tabindex="-1" role="dialog" id="updateConfirmation">
    <div class="modal-dialog modal-dialog-centered" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Confirm Milestone Update</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to update the milestone?</p>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
            Cancel
          </button>
          <button type="button" class="btn nav-color-btn" @click="updateMilestone">
            Update
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
    background: var(--navbar-bg);
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
    box-shadow: 0 0 0 0.2rem rgba(21, 153, 87, 0.15);
    transform: translateY(-1px);
  }

  .btn-gradient {
    background: var(--navbar-bg);
    border: none;
    color: white;
    transition: all 0.3s ease;
    font-weight: 500;
    letter-spacing: 0.5px;
    border-radius: 10px;
  }

  .btn-gradient:hover {
    background: rgb(from var(--navbar-bg) r g b / 0.8);
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  }

  .form-label {
    color: var(--navbar-bg);
    margin-bottom: 8px;
    font-size: 1.1rem;
  }
</style>
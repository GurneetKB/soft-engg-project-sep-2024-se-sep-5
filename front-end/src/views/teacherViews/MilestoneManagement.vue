<script setup>
import { ref, onMounted } from 'vue'

// reactive state
const count = ref(0)

// functions that mutate state and trigger updates
function increment() {
  count.value++
}

// lifecycle hooks
onMounted(() => {
  console.log(`The initial count is ${count.value}.`)
})
</script>


<template>
     <section class="py-5">

<div class="row ">
  <div class="col-sm-6">
    <div class="card hero-section text-white py-5 rounded">
      <div class="card-body">
        <h2 style="text-align:center" class="card-title">Total Registered Students</h2>
        <a href="#" class="btn btn-primary">234</a>
      </div>
    </div>
  </div>
  <div class="col-sm-6">
    <div class="card hero-section text-white py-5 rounded">
      <div class="card-body">
        <h2 style="text-align:center" class="card-title">Total Number of Teams</h2>
        <a href="#" class="btn btn-primary">50</a>
      </div>
    </div>
  </div>
</div>
     </section>

     <section class="py-5 ">
        <div class="container hero-section text-white py-5 rounded">
        <div >
            <h2 style="text-align:center;" class="p-2" >Milestones</h2>
        </div>
        <h5 class="p-2">Milestone 1</h5>

        <div class="progress">
    
  <div class="progress-bar bg-success" role="progressbar" style="width: 100%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
</div>
<br>
<h5 class="p-2">Milestone 2</h5>

<div class="progress">
  <div class="progress-bar bg-warning" role="progressbar" style="width: 50%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
</div>
<br>
<h5 class="p-2">Milestone 3</h5>

<div class="progress">
  <div class="progress-bar bg-danger" role="progressbar" style="width: 10%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
</div>
<br>
<h5 class="p-2">Milestone 4</h5>
<div class="progress">
  <div class="progress-bar bg-light" role="progressbar" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
</div>
<br>
<h5 class="p-2">Milestone 5</h5>

<div class="progress">
  <div class="progress-bar bg-light" role="progressbar" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
</div>
</div>
</section>
</template>


<style scoped>
/* Hero Section Styling with new colors */
.hero-section {
  background: linear-gradient(135deg, #6a5880, #00695c);
}

/* Card Styling */
.card {
  transition: transform 0.3s ease;
}
.card:hover {
  transform: translateY(-5px);
}
</style>

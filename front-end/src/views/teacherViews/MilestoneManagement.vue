<template>
  <section class="py-5">
    <div class="container px-4">
      <div class="row g-4 justify-content-center mx-0">
        <div class="col-sm-5 px-2">
          <div class="stats-card text-white rounded-lg">
            <div class="card-body d-flex flex-column align-items-center">
              <h2 class="card-title fw-bold mb-4">Total Registered Students</h2>
              <div class="stats-number">234</div>
            </div>
          </div>
        </div>
        <div class="col-sm-5 px-2">
          <div class="stats-card text-white rounded-lg">
            <div class="card-body d-flex flex-column align-items-center">
              <h2 class="card-title fw-bold mb-4">Total Number of Teams</h2>
              <div class="stats-number">50</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="py-5">
    <div class="container hero-section text-white py-5 rounded-lg px-4">
      <div class="mb-5">
        <h2 class="text-center main-title">Milestones</h2>
      </div>
      <div class="milestone-wrapper">
        <div class="milestone-item mb-4">
          <h5 class="milestone-title">Milestone 1</h5>
          <div class="progress">
            <div
              class="progress-bar bg-success"
              role="progressbar"
              style="width: 100%"
            ></div>
          </div>
        </div>

        <div class="milestone-item mb-4">
          <h5 class="milestone-title">Milestone 2</h5>
          <div class="progress">
            <div
              class="progress-bar bg-warning"
              role="progressbar"
              style="width: 50%"
            ></div>
          </div>
        </div>

        <div class="milestone-item mb-4">
          <h5 class="milestone-title">Milestone 3</h5>
          <div class="progress">
            <div
              class="progress-bar bg-danger"
              role="progressbar"
              style="width: 10%"
            ></div>
          </div>
        </div>

        <div class="milestone-item mb-4">
          <h5 class="milestone-title">Milestone 4</h5>
          <div class="progress">
            <div
              class="progress-bar bg-light"
              role="progressbar"
              style="width: 0%"
            ></div>
          </div>
        </div>

        <div class="milestone-item mb-4">
          <h5 class="milestone-title">Milestone 5</h5>
          <div class="progress">
            <div
              class="progress-bar bg-light"
              role="progressbar"
              style="width: 0%"
            ></div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero-section {
  background: linear-gradient(135deg, #6a5880, #00695c);
  border-radius: 20px;
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
}

.main-title {
  font-size: 2.5rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 2px;
  position: relative;
  padding-bottom: 15px;
}

.main-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100px;
  height: 3px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 2px;
}

.stats-card {
  background: linear-gradient(135deg, #6a5880, #00695c);
  padding: 2rem;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border-radius: 15px;
}

.stats-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
}

.stats-number {
  font-size: 3.5rem;
  font-weight: bold;
  padding: 1.5rem 2.5rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.milestone-wrapper {
  max-width: 700px;
  margin: 0 auto;
  padding: 0 20px;
}

.milestone-item {
  background: rgba(255, 255, 255, 0.05);
  padding: 20px;
  border-radius: 15px;
  transition: all 0.3s ease;
}

.milestone-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(5px);
}

.milestone-title {
  font-weight: 600;
  margin-bottom: 15px;
  font-size: 1.2rem;
}

.progress {
  height: 1.2rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  overflow: hidden;
}

.progress-bar {
  transition: width 1s ease-in-out;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
}

.card-title {
  font-size: 1.4rem;
  text-align: center;
}
</style>

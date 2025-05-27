<template>
    <div class="error-page">
      <Navbar />
      <h1>404</h1>
      <p>Oops! The page you're looking for doesn't exist.</p>
      <router-link to="/">Go to Home</router-link>
    </div>
  </template>
  <script>
  import Navbar from '@/components/Navbar.vue';
  export default {
    components: { Navbar },   
    }
  </script>
  <style scoped>
  .error-page {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    text-align: center;
    background-color: #f8f9fa;
  }
  
  h1 {
    font-size: 6rem;
    color: #d9534f;
  }
  
  p {
    font-size: 1.5rem;
    color: #333;
  }
  
  a {
    margin-top: 1rem;
    font-size: 1.2rem;
    color: #007bff;
    text-decoration: none;
  }
  
  a:hover {
    text-decoration: underline;
  }
  </style>
  
<!-- Success.vue -->
<template>
    <div class="container-fluid success-page">
      <Navbar :cart-count="cartCount" />
      <div class="content">
        <div class="success-card" v-if="!loading && paymentVerified">
          <i class="bi bi-check-circle" style="font-size: 4rem; color: #2d6a4f;"></i>
          <h2>Payment Successful!</h2>
          <p>Your quizzes have been successfully purchased.</p>
          <router-link to="/user-dashboard" class="btn btn-primary">
            Back to Dashboard
          </router-link>
        </div>
        <div class="error-card" v-else-if="!loading && !paymentVerified">
          <i class="bi bi-x-circle" style="font-size: 4rem; color: #d00000;"></i>
          <h2>Payment Failed</h2>
          <p>There was an issue processing your payment. Please try again.</p>
          <router-link to="/cart" class="btn btn-danger">Back to Cart</router-link>
        </div>
        <div class="spinner-border text-primary" role="status" v-else>
          <span class="visually-hidden">Verifying...</span>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import Navbar from '@/components/Navbar.vue';
  import { useStore } from 'vuex';
  import { useRouter, useRoute } from 'vue-router';
  
  const BASE_URL = `${import.meta.env.VITE_BASE_URL}/api`;
  
  export default {
    components: { Navbar },
    setup() {
      const store = useStore();
      const router = useRouter();
      const route = useRoute();
      return { store, router, route };
    },
    data() {
      return {
        cartCount: 0,
        loading: true,
        paymentVerified: false,
      };
    },
    async created() {
      const access_token = this.store.state.access_token;
      const role = this.store.state.role;
  
      if (!access_token || role !== 'user') {
        this.router.push('/login');
        return;
      }
  
      const sessionId = this.route.query.session_id;
      if (sessionId) {
        await this.verifyPayment(sessionId);
      } else {
        this.router.push('/cart');
      }
      this.loading = false;
    },
    methods: {
      async verifyPayment(sessionId) {
        try {
          const access_token = this.store.state.access_token;
          const response = await axios.get(`${BASE_URL}/dashboard/user/cart/verify-payment/${sessionId}`, {
            headers: { Authorization: `Bearer ${access_token}` },
          });
          
          if (response.status === 200) {
            this.paymentVerified = true;
            this.cartCount = 0;
            this.store.commit('updateCartCount', 0);
          } else if (response.status === 202) {
            // Payment still processing, redirect to cart
            this.router.push('/cart');
          } else {
            this.paymentVerified = false;
          }
        } catch (error) {
          if (error.response?.status === 401) {
            await this.handleTokenRefresh();
            await this.verifyPayment(sessionId);
          } else {
            console.error('Payment verification failed:', error);
            this.paymentVerified = false;
          }
        }
      },
      async handleTokenRefresh() {
        try {
          await this.store.dispatch('refreshToken');
        } catch (error) {
          this.store.commit('clearAuth');
          this.router.push('/login');
        }
      },
    },
  };
  </script>
  
  <style scoped>
  .success-page {
    min-height: 100vh;
    background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f0 100%);
  }
  
  .content {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: calc(100vh - 70px);
  }
  
  .success-card, .error-card {
    background: white;
    padding: 40px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  }
  
  .btn-primary {
    background: linear-gradient(135deg, #52b788, #2d6a4f);
    border: none;
    padding: 10px 20px;
    color: white;
    border-radius: 6px;
  }
  
  .btn-primary:hover {
    background: linear-gradient(135deg, #2d6a4f, #1a3c34);
  }
  
  .btn-danger {
    background: linear-gradient(135deg, #ff6b6b, #d00000);
    border: none;
    padding: 10px 20px;
    color: white;
    border-radius: 6px;
  }
  
  .btn-danger:hover {
    background: linear-gradient(135deg, #d00000, #9d0208);
  }
  </style>
  
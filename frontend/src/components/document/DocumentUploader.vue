<script setup lang="ts">
import { ref } from 'vue';
import { useStore } from 'vuex';
import AlertMessage from '../common/AlertMessage.vue';

const store = useStore();
const file = ref<File | null>(null);
const isUploading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

const onFileChange = (event: Event) => {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files.length > 0) {
    const selectedFile = input.files[0];
    
    // Check if file is a PDF
    if (!selectedFile.name.toLowerCase().endsWith('.pdf')) {
      errorMessage.value = 'Only PDF files are allowed.';
      file.value = null;
      return;
    }
    
    file.value = selectedFile;
    errorMessage.value = '';
  }
};

const uploadDocument = async () => {
  if (!file.value) return;
  
  isUploading.value = true;
  errorMessage.value = '';
  successMessage.value = '';
  
  try {
    const result = await store.dispatch('queries/uploadDocument', file.value);
    
    if (result) {
      successMessage.value = `Document ${file.value.name} uploaded successfully!`;
      file.value = null;
      
      // Reset the file input
      const fileInput = document.getElementById('documentFile') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
    } else {
      errorMessage.value = 'Failed to upload document. Please try again.';
    }
  } catch (error: any) {
    errorMessage.value = error.message || 'Upload failed. Please try again.';
  } finally {
    isUploading.value = false;
  }
};
</script>

<template>
  <div class="document-uploader card">
    <div class="card-header bg-accent">
      <div class="d-flex justify-content-between align-items-center">
        <div class="d-flex align-items-center">
          <i class="bi bi-upload me-2"></i>
          <span class="fw-bold">Upload Document</span>
        </div>
      </div>
    </div>
    <div class="card-body">
      <AlertMessage 
        v-if="errorMessage" 
        type="danger" 
        :message="errorMessage" 
        :auto-close="true" 
      />
      <AlertMessage 
        v-if="successMessage" 
        type="success" 
        :message="successMessage" 
        :auto-close="true" 
      />
      
      <div class="mb-3">
        <label for="documentFile" class="form-label">Select PDF Document</label>
        <input 
          type="file" 
          class="form-control" 
          id="documentFile" 
          accept=".pdf" 
          @change="onFileChange"
          :disabled="isUploading"
        >
        <div class="form-text">Only PDF files are supported.</div>
      </div>
      
      <div v-if="file" class="selected-file mb-3">
        <div class="d-flex align-items-center">
          <i class="bi bi-file-pdf me-2 text-danger"></i>
          <span>{{ file.name }}</span>
          <span class="ms-2 text-muted">{{ (file.size / 1024).toFixed(1) }} KB</span>
        </div>
      </div>
      
      <button 
        class="btn btn-accent" 
        @click="uploadDocument" 
        :disabled="!file || isUploading"
      >
        <span v-if="isUploading">
          <span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
          Uploading...
        </span>
        <span v-else>
          <i class="bi bi-cloud-arrow-up me-1"></i> Upload Document
        </span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.document-uploader {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card-header.bg-accent {
  background-color: var(--accent) !important;
  color: white;
}

.selected-file {
  background-color: var(--neutral-100);
  padding: 12px;
  border-radius: 8px;
}

.btn-accent {
  background-color: var(--accent);
  border-color: var(--accent);
  color: white;
}

.btn-accent:hover, .btn-accent:focus {
  background-color: var(--accent-dark);
  border-color: var(--accent-dark);
  color: white;
}

.btn-accent:disabled {
  background-color: var(--accent-light);
  border-color: var(--accent-light);
}
</style>
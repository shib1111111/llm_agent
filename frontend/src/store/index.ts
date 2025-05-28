import { createStore } from 'vuex';
import auth from './modules/auth';
import queries from './modules/queries';

export default createStore({
  modules: {
    auth,
    queries
  }
});
import axios from "axios";

export default {
	namespaced: true,
	state: {
  		user: JSON.parse(localStorage.getItem('user')) || '',
		profile: null
	},
	mutations: {
	  	auth(state, user){
	  		const token = user.token
		    state.user = user
			localStorage.setItem('user', JSON.stringify(user))
	  	},
	  	unauth(state){
	    	state.user = ''
	    	state.profile = ''
			localStorage.removeItem('user')
	  	},
		sync(state, user){
		    state.user.username = user.username
		    state.profile.username = user.username
			localStorage.setItem('user', JSON.stringify(state.user))
		},
		extra(state, data){
			state.profile = data
		}
	},
	actions: {
	  	login({commit}, payload){
	        return new Promise((resolve, reject) => {
				this._vm.$api
				.get('auth', {auth: payload})
				.then(resp => {
					commit('auth', resp.data)
	                resolve(resp)
				})
				.catch(err => {
					console.log(err.response.data)
	                reject(err)
				})
	        })
			.catch(err => {})
	    },
	    register({commit}, payload){
	        return new Promise((resolve, reject) => {
				this._vm.$api
				.post('create', payload)
				.then(resp => {
					this.dispatch('auth/login', payload);
	                resolve(resp)
				})
				.catch(err => {
					console.log(err.response.data)
	                reject(err)
				})
	        })
			.catch(err => {})
	    },
	  	refresh({commit}, payload){
			commit('sync', payload)
	  	},
	  	logout({commit}){
			commit('unauth')
	  	},
	    profile({commit, state}){
            return new Promise((resolve, reject) => {
                this._vm.$api
				.get(`/get/${state.user.public_id}`, {
                    headers: {
                        'x-access-token': `${state.user.token}`,
                    }
                })
                .then(resp => {
					commit('extra', resp.data.user)
                    resolve(resp)
                })
                .catch(err => {
                    console.log(err.response.data)
                    reject(err)
                })
            })
			.catch(err => {})
	    },
	},
	getters : {
        isAuth: state => !!state.user.token,
        getUser: state => state.user,
        getProfile: state => state.profile,
	}
}
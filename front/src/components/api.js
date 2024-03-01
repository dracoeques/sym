import axios from "axios";

export default class Api {

    constructor(url_base=""){

        
        const base = window.location.origin;
        console.log("base", base);
        
        if (base === "http://localhost:5173" || base === "http://localhost:5174"){
            url_base = "http://localhost:8000"
        } 
        this.api = axios.create({
            baseURL: url_base,
        });
        console.log("API initialized",url_base);
        this.api.defaults.headers.common['X-api-key'] = this.getItem("authtoken");

    }

    getUrlParam(name, url){
        if (!url) url = location.href;
        name = name.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
        var regexS = "[\\?&]"+name+"=([^&#]*)";
        var regex = new RegExp( regexS );
        var results = regex.exec( url );
        return results == null ? null : results[1];
    }

    getItem(key){
        try {
            if(localStorage.hasOwnProperty(key)){
                return localStorage[key];
            }
        } catch (error) {
            console.error(error.message);
            return null; 
        }
    }

    setItem(key, item){
        try {
            localStorage.setItem(key, item);
            return true;
        } catch (error) {
            console.error(error.message);
            return false; 
        }
    }

    clearStorage(){
        localStorage.clear();
    }

    logout(){
        this.clearStorage();
    }

    async login(payload){
        try {
            const response = await this.api.post('/api/users/login', payload);
            //console.log("response: ", response);
            this.setItem("authtoken", response.data.token);
            this.api.defaults.headers.common['X-api-key'] = response.data.token;
            return response.data;
        } catch (error) {
            throw error;
        }
        
    }

    async me(){
        try {
            const response = await this.api.get('/api/users/me');
            return response.data;
        } catch (error) {
            throw error;
        }
    }

    async loadProfiles(){
        try {
            const response = await this.api.get('/api/users/profiles');
            return response.data;
        } catch (error) {
            throw error;
        }
    }

    async savePromptFlow(payload){
        try {
            const response = await this.api.post('/api/promptflow', payload);
            return response.data;
        } catch (error) {
            throw error;
        }
    }

    async loadPromptFlow(flow_id){
        try {
            const response = await this.api.get(`/api/promptflow/${flow_id}`);
            return response.data;
        } catch (error) {
            throw error;
        }
    }

    async loadPromptFlows(){

    
        try {
            const response = await this.api.get("/api/promptflows/");
            return response.data;
        } catch (error) {
            throw error;
        }
    }

    async savePromptLib(payload){
        try {
            const response = await this.api.post('/api/promptlib', payload);
            return response.data;
        } catch (error) {
            throw error;
        }
    }

    async loadPromptLib(lib_id){
        try {
            const response = await this.api.get(`/api/promptlib/${lib_id}`);
            return response.data;
        } catch (error) {
            throw error;
        }
    }

    async loadPromptViewCategory(category, subcategory){
        try {
            const response = await this.api.get(`/api/prompt-view-category?category=${category}&subcategory=${subcategory}`);
            return response.data;
        } catch (error) {
            throw error;
        }
    }

    async loadCircleCategories(){
        try {
            const response = await this.api.get(`/api/circle-categories`);
            return response.data;
        } catch (error) {
            throw error;
        }
    }

    async loadArchetypeCategories(){
        try {
            const response = await this.api.get(`/api/flower-categories`);
            return response.data;
        } catch (error) {
            throw error;
        }
    }

    async loadPromptDeck(id_deck){
        try {
            const response = await this.api.get(`/api/prompt-deck/${id_deck}`);
            return response.data;
        } catch (error) {
            throw error;
        }
    }

    async doPersonalKVSearch(topic){
        try {
            const response = await this.api.get(`/api/get_personal_kv/?topic=${topic}`);
            return response.data;
        } catch (error) {
            throw error;
        }
    }

    async votePersonalKV(payload){
        try {
            const response = await this.api.post(`/api/vote_personal_kv/`, payload);
            return response.data;
        } catch (error) {
            throw error;
        }
    }

    async runKVETL(){
        try {
            const response = await this.api.post(`/api/run_personal_kv_etl/`, {});
            return response.data;
        } catch (error) {
            throw error;
        }
    }

    async getDiscoveryItems(page){
        try {
            const response = await this.api.get(`/api/discover/?page=${page}`);
            return response.data;
        } catch (error) {
            throw error;
        }
    }

    async getCustomDiscoveryFeedItems(feed_id, page){
        try {
            const response = await this.api.get(`/api/discovery-feed-items/${feed_id}?page=${page}`);
            return response.data;
        } catch (error) {
            throw error;
        }
    }

    async getPersonalizedDiscoveryFeedItems(feed_id, page){
        try {
            const response = await this.api.get(`/api/personalized-feed-items/${feed_id}?page=${page}`);
            return response.data;
        } catch (error) {
            throw error;
        }
    }

    async getDiscoveryFeed(feed_id){
        try {
            const response = await this.api.get(`/api/discovery-feed/${feed_id}`);
            return response.data;
        } catch (error) {
            throw error;
        }
    }

    

    async getDiscoveryTopics(topics, page){
        try {
            const response = await this.api.get(`/api/discover-topics?topics=${topics}&page=${page}`);
            return response.data;
        } catch (error) {
            throw error;
        }
    }

    async createDiscoveryFeed(payload){
        try {
            const response = await this.api.post(`/api/discovery-feed`, payload);
            return response.data;
        } catch (error) {
            throw error;
        }
    }

    async chatWithMediaItem(payload){
        try {
            const response = await this.api.post(`/api/media-item-chat`, payload);
            return response.data;
        } catch (error) {
            throw error;
        }
    }

    async getFlowStatus(flows){
        try {
            const response = await this.api.post(`/api/flow-status`, flows);
            return response.data;
        } catch (error) {
            throw error;
        }
    }

    async resetFlowCompletions(flows){
        try {
            const response = await this.api.post(`/api/flow-reset-completed-status`, flows);
            return response.data;
        } catch (error) {
            throw error;
        }
    }

}
import react from "react"

import Api from "./api.js";

export default class Login extends react.Component {

    constructor(props){
        super(props);
        this.state = {
            api:new Api(),
            
            email:"",
            password:"",
            redirect_url:"/app/flower", //"/app/prompt-flow-designer", //"/app/flower",
            error:null,
            pageHeight:window.innerHeight,


        }
        this.onEmailChange = this.onEmailChange.bind(this);
        this.onPasswordChange = this.onPasswordChange.bind(this);
        this.submitLogin = this.submitLogin.bind(this);
        this.gotoRegister = this.gotoRegister.bind(this);
    }

    onEmailChange(e){
        this.setState({email:e.target.value});
    }

    onPasswordChange(e){
        this.setState({password:e.target.value});
    }

    gotoRegister(){
        //this.state.routeFunc("register");

    }

    async submitLogin(){
        const payload = {"email":this.state.email, "password":this.state.password};
        try {
            const token = await this.state.api.login(payload);
            console.log('login:', token);
            window.location.href = this.state.redirect_url;

            
        } catch (error) {
            console.error('Error submitLogin:', error, error.response.data.Message);
            this.setState({"error":error.response.data.Message});
        }
    }

    render(){

        let errorComponent = (<div></div>)
        if (this.state.error !== null){
            errorComponent = (<span className="text-danger">{this.state.error}</span>)
        }

        return(

            <div className="bg-dark" style={{height:this.state.pageHeight}}>
                <br></br>
                <div className="row ">
                    <div className="col-sm-4">
                    
                    </div>
                    <div className="col-sm-4 main-content" style={{minHeight:"400px"}} >
                        
                        <div className="card mb-3 nopad pbg">
                        <h3 className="card-header">Login</h3>
                        <div className="card-body pfg">
                        <form>
                        <fieldset>
                            
                            <div className="form-group">
                                <label className="form-label mt-4">Email Address</label>
                                <input onChange={this.onEmailChange} type="email" className="form-control" id="exampleInputEmail1" aria-describedby="emailHelp" placeholder="Enter email" />
                                <small id="emailHelp" className="form-text text-muted"></small>
                            </div>
                            <div className="form-group">
                                <label className="form-label mt-4">Password</label>
                                <input onChange={this.onPasswordChange} type="password" className="form-control" id="exampleInputPassword1" placeholder="Password" />
                            </div>
                            <hr></hr>
                            <div className="row">
                                <div className="col-sm-3">
                                    <button onClick={this.submitLogin} type="button" className="btn btn-success">Submit</button>
                                </div>
                                <div className="col-sm-6">
                                {errorComponent}
                                </div>
                                <div className="col-sm-3 ">
                                {/* <button onClick={this.gotoRegister} type="button" className="btn btn-outline-secondary">Register</button> */}
                                </div>
                                
                            </div>

                        </fieldset>
                        </form>
                        </div>
                        <div className="card-footer">
                           
                        </div>
                        </div>
                    </div>
                    <div className="col-sm-4" >
                        
                    </div>
                </div>

            </div>
        )

    }
}
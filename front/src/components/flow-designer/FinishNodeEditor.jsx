import React from 'react';

class FinishNodeEditor extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            data:{
                id:props.id,
                outro_message: props.outro_message ? props.outro_message : "",
            },
            
            
            
        }
        
        this.updateOutroMessage = this.updateOutroMessage.bind(this);
    }

    updateOutroMessage(e){

        let data = this.state.data;
        data.outro_message = e.target.value
        this.props.updateNodeData(data);

        // this.setState({question:e.target.value}, () => {
        //     this.props.updateNodeData(this.state);
        // });
    }

    render(){
        return (
            <div>
                <h3 className="text-light">Finish Node</h3>
                

                <h5 className='text-light'>Outro Message</h5>
                <textarea
                    className="form-control" 
                    rows="3"

                    value={this.props.outro_message}
                    onChange={this.updateOutroMessage}
                ></textarea>
                
                <hr></hr>

                
                
            </div>
        )
    }


}

export default FinishNodeEditor;
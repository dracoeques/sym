import React from 'react';

import Creatable from 'react-select/creatable';

class ComboBox extends React.Component {

    constructor(props){
        super(props);
        this.state = {
            promptId:this.props.promptId,
            selectedOption:this.props.selectedOption,
            variableKey:this.props.variableKey,
            options:this.props.options,
        }
        this.handleChange = this.handleChange.bind(this);

    }

    handleChange = (selectedOption) => {
        this.setState({ selectedOption }, () => {
            this.props.updateValue(this.state);
        });
        console.log(`Option selected:`, selectedOption);

        
    };

    render(){
        return (
            <Creatable
                value={this.state.selectedOption}
                onChange={this.handleChange}
                options={this.state.options}
                isClearable
                isSearchable
            />
        );
    }

}

export default ComboBox;
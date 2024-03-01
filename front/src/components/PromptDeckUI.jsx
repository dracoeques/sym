import React from 'react';
// import 'style.css';  // assuming the CSS above is saved in 'style.css'

import PromptFlowChat from './PromptFlowChat';

import Dropdown from 'react-bootstrap/Dropdown';

import 'bootswatch/dist/lux/bootstrap.min.css'; // Added this :boom:

import '../App.css'

class PromptDeckUI extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isAddingColumn:false,
      isPrompting:false,
      columns: [
        {
          id:1,
          name:"Example",
          flow_id:23,
        }
      ],
      innerHeight:window.innerHeight,
    };

    this.handleResize = this.handleResize.bind(this);
    this.addColumn = this.addColumn.bind(this);
    this.startAddColumn = this.startAddColumn.bind(this);
  }


  componentDidMount(){

    

      window.addEventListener('resize', this.handleResize);


  }

  handleResize(){
      
      const innerHeight = window.innerHeight;
      //console.log("resize",innerHeight);
      this.setState({innerHeight:innerHeight})
  }

  addColumn() {
    this.setState(prevState => ({
      isAddingColumn:false,
      columns: [...prevState.columns, { id: prevState.columns.length + 1 }]
    }));
  }

  removeColumn(x){
    console.log("removeColumn", x);
    let newColumns = [];
    for (var i in this.state.columns){
      const col = this.state.columns[i];
      if (col.id === x){
        console.log("remove column", x);
        continue
      } else {
        newColumns.push(col);
      }
    }
    this.setState({
      columns:newColumns,
    })
  }

  startAddColumn(){
    this.setState({isAddingColumn:!this.state.isAddingColumn});
  }

  renderControls(){
    const contentHeight = this.state.innerHeight;
    const controlsHeight = 500;

    let deckListHeight = 300;
    if (contentHeight > 700) {
        deckListHeight = contentHeight - controlsHeight;
    }
    return (
      <div className='deck-controls'> 
            <br></br>
            <div className='row' style={{padding:10}}>
                <div className='col-sm-1'></div>
                <div className='col-sm-2'>
                    <img 
                        width="60" 
                        src="https://cdn.dribbble.com/users/829077/screenshots/5900353/robot2.gif"
                        style={{
                            borderRadius: 20,
                        
                        
                        }}
                        
                    ></img>
                </div>
                <div className='col-sm-6'
                    style={{
                        paddingLeft:20,
                    }}
                >
                    <h5 className='text-light'>Blake Allen</h5>
                    <h6 className='text-light'>@blakedallen</h6>
                </div>
                <div className='col-sm-2'
                    style={{cursor:"pointer"}}
                >
                <button className='btn btn-primary '
                    style={{borderRadius: 10}}
                >⚙️</button>
                </div>
            </div>
            <hr></hr>
            <div className='row' style={{padding:10}}>
                <div className='col-sm-1'></div>
                <div className='col-sm-9'>
                <button 
                    className='btn btn-block btn-info' 
                    style={{borderRadius: 20, width:"100%"}}>
                        <h3 className="text-light"
                            style={{marginBottom:0}}
                        >
                            Prompt</h3></button>
                </div>
                <div className='col-sm-1'></div>
                
            </div>
            <div className='row' style={{padding:10}}>
                <div className='col-sm-6'>
                <button 
                    className='btn btn-primary' 
                    style={{borderRadius: 20}}
                    onClick={this.startAddColumn}
                    >
                        
                        + Add column</button>

                </div>
                <div className='col-sm-6'>
                <button 
                    className='btn btn-primary' 
                    style={{borderRadius: 20}}>
                    
                    <span style={{marginRight:4}}>🔍 </span> <span>Search</span></button>
                </div>
                <div className='col-sm-2'></div>
                
            </div>
            <hr></hr>
            <div className='row' >
                <div className='col-sm-2'>
                <button 
                    className='btn btn-primary disabled' 
                    style={{
                            borderRadius: 20,
                            marginLeft: 6,
                        }}>
                        
                        Decks</button>
                </div>
                <div className='col-sm-5'>
                
                </div>
                <div className='col-sm-5'>
                <button 
                    className='btn btn-primary' 
                    style={{borderRadius: 20}}>
                        
                        + New Deck</button>
                </div>
                
            </div>

            <div className='row deck-list' 
                            style={{
                                paddingLeft: 8,
                                height:deckListHeight,
                                overflowY:"scroll",
                            }}>
                            <ul
                              className=''
                            >
                                
                                <li
                                        className='btn btn-primary' 
                                        style={{
                                            borderRadius: 20, 
                                            textAlign:"left",
                                            height: 50,
                                        }}>
                                    <span style={{marginRight:4}}>🚀 </span> <span>Direct Response Copy</span>
                                    
                                </li>
                                <li>
                                    <button 
                                    className='btn btn-primary' 
                                    style={{
                                        borderRadius: 20, 
                                        textAlign:"left",
                                        height: 50,
                                    }}>
                                    
                                    <span style={{marginRight:4}}>🌋 </span> <span>Emotional Intelligence</span>
                                    </button>
                                </li>
                                <li>
                                    <button 
                                    className='btn btn-primary' 
                                    style={{
                                        borderRadius: 20, 
                                        textAlign:"left",
                                        height: 50,
                                    }}>
                                    
                                    <span style={{marginRight:4}}>🏝️ </span> <span>Travel</span>
                                    </button>
                                </li>
                                <li>
                                    <button 
                                    className='btn btn-primary' 
                                    style={{
                                        borderRadius: 20, 
                                        textAlign:"left",
                                        height: 50,
                                    }}>
                                    
                                    <span style={{marginRight:4}}>💡 </span> <span>Ideas</span>
                                    </button>
                                </li>

                                
                            </ul>
                            
                            
                        </div>

                        
                    
                        <div className='sym-footer'
                        
                        >
                        <hr></hr>
                        <img 
                            style={{
                                paddingLeft: 32,
                            }}
                            width={100}
                            src="http://localhost:8000/static/sym.png">
                        </img>
                        </div>  
        </div> 
      
    )
  }

  renderAddColumn(){
    return (
      <div
        className='bg-primary'
        style={{
          height:this.state.innerHeight,
          minWidth: 400,
          width:400,
          padding:20,
        }}
      >
        <div className='container'>
          <div className='row'>
            <div className='col-sm-9'>
              <h2 className='text-light'>Add column</h2>
            </div>
            <div className='col-sm-3'>
              <button className="btn btn-primary" onClick={this.startAddColumn}>🗑️</button>
            </div>
          </div>

          {/* search */}

          <h4 className='text-light'>Choose one</h4>

          

          <ul>
            <li
                className='btn btn-primary' 
                style={{
                    borderRadius: 20, 
                    textAlign:"left",
                    height: 50,
                }}
                onClick={this.addColumn}
            >
                                    <span style={{marginRight:4}}> 🤖</span> <span>New ChatGPT Agent</span>
            </li>
          <li
                                        className='btn btn-primary' 
                                        style={{
                                            borderRadius: 20, 
                                            textAlign:"left",
                                            height: 50,
                                        }}>
                                    <span style={{marginRight:4}}>🌸 </span> <span>Explore Using Flower</span>
                                    </li>
          </ul>
        </div>
        


      </div>

    )
  }

  renderColumns(){
    return this.state.columns.map(column => (
      <div key={column.id} className="deck-column bg-primary"
      style={{
        height:this.state.innerHeight,
      }}
      >
        <div className='row' style={{padding:20}}>
          <div className='col-sm-10'>
            {column.name}
          </div>


          <div className='col-sm-2'>
          <Dropdown>
            <Dropdown.Toggle  id="dropdown-basic">
            ⚙️
            </Dropdown.Toggle>

            <Dropdown.Menu>
              <Dropdown.Item href="#/action-1">Action</Dropdown.Item>
              <Dropdown.Item href="#/action-2">Another action</Dropdown.Item>
              <Dropdown.Item onClick={() => this.removeColumn(column.id)}>🗑️ Remove Column</Dropdown.Item>
            </Dropdown.Menu>
          </Dropdown>

          
          </div>
        </div>
        
        
          
        
      <div
        style={{
          height:this.state.innerHeight - 100, 
          
        }}
        className='bg-light'
      >
        <PromptFlowChat 

                                
                                height={this.state.innerHeight - 100}
                                promptFlowId={92}
                                doResize={false}
                            />
      </div>
      </div>
    ))
  }

  render() {

    let columnAdder = (<div></div>);
    if (this.state.isAddingColumn){
      columnAdder = this.renderAddColumn();
    }


    

    return (
        <div className='deck-body'>
      <div className="deck-container">
        <div className="deck-left-column bg-primary"
          style={{
            height:this.state.innerHeight,
            minWidth:400,
          }}
        >
          {this.renderControls()}
          
        </div>
        <div className="deck-content-area">
          {columnAdder}
          {this.renderColumns()}
        </div>
      </div>
      </div>
    );
  }
}

export default PromptDeckUI;

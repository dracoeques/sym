import React from 'react';

import { Editor } from 'react-draft-wysiwyg';
import '../../node_modules/react-draft-wysiwyg/dist/react-draft-wysiwyg.css';

import draftToHtml from 'draftjs-to-html';
import draftToMarkdown from 'draftjs-to-markdown';
import { convertToRaw, convertFromRaw } from 'draft-js';

import Api from './api.js';


import { withRouter } from './utils.jsx';



import 'bootswatch/dist/lux/bootstrap.min.css'; // Added this :boom:

const defaultContent = {"entityMap":{},"blocks":[{"key":"637gr","text":"Initialized from content state.","type":"unstyled","depth":0,"inlineStyleRanges":[],"entityRanges":[],"data":{}}]};


class EditorComponent extends React.Component {

  

  constructor(props){
    super(props);
    this.state = {
      api:new Api(),
      sidebarHeight:window.innerHeight,
      contentState: defaultContent,
    }

    this.onContentStateChange = this.onContentStateChange.bind(this);
    this.onSave = this.onSave.bind(this);
  }

  onSave(){
    console.log("json output", this.state.contentState);

    let markup = draftToMarkdown(this.state.contentState);
    //not sure why, but spaces are denoted as \s and newlines \\s
    //convert them to normal spaces and newlines here
    markup  = markup.replace(/\\s/g, " ");
    markup  = markup.replace(/\\s\\s/g, "\n");

    console.log("markup output", markup);

    let htmlOutput = draftToHtml(this.state.contentState);
    console.log("html output", htmlOutput);

  }

  onContentStateChange(contentState) {
    //console.log(content)
    //const contentState = convertFromRaw(content);
    this.setState({
      contentState:contentState,
    });
  }

  render(){

    return (
      
      <div className='container-fluid'>
          <div className='row'>
              <div className='col-sm-2 bg-primary nomargin'
                  style={{
                      height:this.state.sidebarHeight,
                      overflowY:"scroll",
                  }}
              >
                  <div>
                      
                          <button onClick={this.onSave}>Save</button>
                     
                  </div>
                
              </div>
              <div className='col-sm-10 bg-white nomargin'>

                <Editor 
                  onContentStateChange={this.onContentStateChange}
                />
                
              </div>
        </div>
      </div>
    )
  }

}


export default withRouter(EditorComponent);
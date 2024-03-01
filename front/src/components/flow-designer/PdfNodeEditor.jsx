import React from 'react';

import { Editor } from 'react-draft-wysiwyg';
import '../../../node_modules/react-draft-wysiwyg/dist/react-draft-wysiwyg.css';

import { draftToMarkdown, markdownToDraft } from 'markdown-draft-js';

// import draftToMarkdown from 'draftjs-to-markdown';
import { EditorState, ContentState, convertToRaw, convertFromRaw } from 'draft-js';

import Api from '../api.js';


import { withRouter } from '../utils.jsx';

import htmlToDraft from 'html-to-draftjs';
import draftToHtml from 'draftjs-to-html';

import 'bootswatch/dist/lux/bootstrap.min.css'; // Added this :boom:

const defaultContent = {"entityMap":{},"blocks":[{"key":"637gr","text":"Initialized from content state.","type":"unstyled","depth":0,"inlineStyleRanges":[],"entityRanges":[],"data":{}}]};


class PDFNodeEditor extends React.Component {

  constructor(props){
    super(props);
    this.state = {
      api:new Api(),
      sidebarHeight:window.innerHeight,
      contentState: defaultContent,
      data: {
        id:props.id,
        html_text: props.html_text ? props.html_text : "<html><html>"
      }
    }

    const html = props.html_text;

    if (html){
      const contentBlock = htmlToDraft(html);
      if (contentBlock) {
          const contentState = ContentState.createFromBlockArray(contentBlock.contentBlocks);
          const editorState = EditorState.createWithContent(contentState);
          this.state.editorState = editorState;
        }
    }

    

    console.log("hello")
    
    console.log("props.html_text", props.html_text);

    // if (props.html_text){
    //     let as_html = htmlToDraft(props.html_text);
    //     console.log(as_html);
    //     this.state.contentState = as_html;
    //     this.state.editorState = EditorState.createWithContent(as_html);
        

    // }

    this.onContentStateChange = this.onContentStateChange.bind(this);
    this.onEditorStateChange = this.onEditorStateChange.bind(this);
    this.onSave = this.onSave.bind(this);
  }

  onSave(){
    let markup = draftToMarkdown(this.state.contentState);
    //not sure why, but spaces are denoted as \s and newlines \\s
    //convert them to normal spaces and newlines here
    markup  = markup.replace(/\\s/g, " ");
    markup  = markup.replace(/\\s\\s/g, "\n");

    console.log("markup output", markup);


  }

  convertToMarkdown1(){
    let markup = draftToMarkdown(this.state.contentState);
    //not sure why, but spaces are denoted as \s and newlines \\s
    //convert them to normal spaces and newlines here
    markup  = markup.replace(/\\s/g, " ");
    markup  = markup.replace(/\\s\\s/g, "\n");

    console.log("markup output", markup);
    return markup;
  }

  convertToMarkdown2(){
    const rawObject = convertToRaw(this.state.contentState);
    let markup = draftToMarkdown(rawObject);
    console.log("markup", markup);
    //not sure why, but spaces are denoted as \s and newlines \\s
    //convert them to normal spaces and newlines here
    // markup  = markup.replace(/\\s/g, " ");
    // markup  = markup.replace(/\\s\\s/g, "\n");

    // console.log("markup output", markup);
    return markup;
  }

  onContentStateChange(contentState) {
    console.log("onContentStateChange",contentState);
    const contentState2 = ContentState.createFromBlockArray(contentState)
    const editorState = EditorState.createWithContent(contentState2);
    //const contentState = convertFromRaw(content);
    this.setState({
      contentState:contentState,
      editorState:editorState,
    }, () => {

    });

    let htmlOutput = draftToHtml(contentState);
    

    let data = this.state.data;
    data.html_text = htmlOutput
    this.props.updateNodeData(data);
  }

  onEditorStateChange(editorState) {

    this.convertToMarkdown1()

    console.log("onEditorStateChange", editorState);
    this.setState({
      editorState,
    },() => {
        

    });

    const html = draftToHtml(convertToRaw(editorState.getCurrentContent()));
    let data = this.state.data;
    data.html_text = html
    this.props.updateNodeData(data);
  };


  render(){

    return (
      
      <div className='container-fluid'>
          <div className='row'>
              <div className='col-sm-12 nomargin'
                  
              >
                <h2 className='text-white'>PDF Editor</h2>
                <div className='bg-white'
                    style={{
                        minHeight:600,
                        overflowY:"scroll",
                    }}
                >
           
                <Editor 
                  editorState={this.state.editorState}
                  //onContentStateChange={this.onContentStateChange}
                  onEditorStateChange={this.onEditorStateChange}
                />
                </div>
              </div>
        </div>
      </div>
    )
  }

}


export default withRouter(PDFNodeEditor);
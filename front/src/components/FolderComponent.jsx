import React, { Component } from 'react';

const defaultFolders = [
    {
        id: '1',
        name: 'Folder 1',
        items: [{"name":'Item 1', "id":1}, {"name":'Item 2', "id":2}],
        open:false,
        subfolders: []
    },
    {
        id: '2',
        name: 'Folder 2',
        items: [],
        open:false,
        subfolders: [
            {
                id: '2.1',
                name: 'Subfolder 1',
                items: [{"name":'SubItem 1', "id":3}, {"name":'SubItem 2', "id":4}],
                open:false,
                subfolders: [] // not currently supported
            }
        ]
    }
]

class FolderComponent extends Component {
    
    constructor(props){
        super(props);
        this.state = {
            folders: this.props.folders ? this.props.folders : defaultFolders,
            folderId2folder:{},
            selectedItem: null,
            draggedItem: null,
        }
    }
    

    componentDidMount(){
        
    }

    handleFolderClick = (folder, e) => {
        // Open or perform action on folder (this can be expanded upon)
        //console.log(`Clicked folder: ${folder.name}`);
        let folders = this.state.folders;
        //console.log(folders);
        
        //toggle open
        //TODO: a better datastructure would make sense here, folders indexed by id, with order as a variable
        //vs needing to traverse, but this is just a quick solution.
        let found = false;
        for (const i in folders){
            const f1 = folders[i];
            if (folder.id === f1.id){
                folders[i]["open"] = !folders[i]["open"];
                found = true;
                break
            }
            // subfolders
            for (const j in folders[i].subfolders){
                const f2 = folders[i].subfolders[j];
                if (folder.id === f2.id){
                    folders[i].subfolders[j]["open"] = !folders[i].subfolders[j]["open"];
                    found = true;
                    break
                }
            }
            //end traversal if found
            if (found === true){
                break
            }
        }
        
        
        this.setState({folders:folders});

    }

    findParentFolder(item){
        const folders = this.state.folders;

        //TODO: a simpler reference to parent folder would suffice
        //...
        for (const i in folders){
            const f = folders[i];

            if (f.items.includes(item)){
                return f
            }
            
            // subfolders
            for (const j in folders[i].subfolders){
                const f2 = folders[i].subfolders[j];
                if (f2.items.includes(item)){
                    return f2
                }
            }
        }
        //nothing found
        return null
    }

    handleDragStart = (item, e) => {
        this.setState({ draggedItem: item });
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', item); // set drag data, this is required for Firefox
    }

    handleDropOnFolder = (folder, e) => {
        e.preventDefault();
        const { draggedItem } = this.state;

        //console.log(folder, this.state.folders);

        // Implement logic to remove item from the original folder and add to the new folder
        if (draggedItem) {
            // Sample logic: (You'd need more robust logic for deeply nested structures)
            const sourceFolder = this.findParentFolder(draggedItem);
            sourceFolder.items = sourceFolder.items.filter(item => item !== draggedItem);

            folder.items.push(draggedItem);

            this.setState({ draggedItem: null }); // Reset the dragged item
        }
    }

    handleDragOver = (e) => {
        e.preventDefault();
    }

    handleItemClick = (item, e) => {
        e.preventDefault();
        //console.log("handleItemClick", item);
        // Update the selectedItem in state
        this.setState({ selectedItem: item });
    }

    addSubfolder = (parentId, name) => {
        // Add a subfolder to the folder with the given parentId
        // (you'd need to implement a recursive search or a better data structure to handle deep nesting)
    }

    editItem = (item, newName) => {
        // Implement editing logic for items
    }

    moveItem = (item, targetFolderId) => {
        // Implement moving logic
    }

    renderFolder = (folder) => {

        let inner = (<div></div>);
        let folderIcon = "📁";

        if (folder.open === true){
            folderIcon = "📂";
            inner = (<ul>
                {folder.items.map(item => (
                    <li key={item.id} 
                        onClick={(e) => this.handleItemClick(item, e)}
                        draggable={true}
                        onDragStart={(e) => this.handleDragStart(item, e)}
                    >{item.name}</li>
                ))}
                {folder.subfolders.map(this.renderFolder)}
            </ul>)
        }

        return (
            <div key={folder.id} 
                style={{cursor:"pointer"}}
            >
                <span 
                    onClick={(e) => this.handleFolderClick(folder, e)}
                    onDrop={(e) => this.handleDropOnFolder(folder, e)}
                    onDragOver={this.handleDragOver}
                >{folderIcon} {folder.name}</span>
                {inner}
            </div>
        );
    }

    render() {

        let folders = this.state.folders.map(this.renderFolder);
        let selectedItem = (<div></div>);

        if (this.state.selectedItem){
            selectedItem = (<span>{this.state.selectedItem.name}</span>)
        }

        return (
            <div className='bg-primary'>
                <div>
                    {folders}
                    
                </div>
            </div>
        );
    }
}

export default FolderComponent;

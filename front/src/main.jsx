import React from 'react';
import ReactDOM from 'react-dom/client'

import * as amplitude from "@amplitude/analytics-browser";


import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";

import './index.css'

// Component imports

import App from './App.jsx'
import CircleView from './components/CircleView.jsx';
import Login from './components/Login.jsx';
import PromptView from './components/PromptView.jsx';
import PromptFlowDesigner from './components/flow-designer/PromptFlowDesigner.jsx';
import PromptFlowDesigner1 from './components/flow-designer/PromptFlowDesigner1.jsx';
import PromptFlowChat from './components/PromptFlowChat.jsx'
import WebsocketTests from './components/WebsocketTests.jsx'
import PromptLibDesigner from './components/PromptLibDesigner.jsx';
import PromptTemplate from './components/PromptTemplate.jsx';
import PromptViewCategory from './components/PromptViewCategory.jsx';
import Dashboard from './components/Dashboard.jsx';

import FolderComponent from './components/FolderComponent.jsx';

import PromptDeck from './components/PromptDeck.jsx';
import PromptDeckUI2 from './components/PromptDeckUI2.jsx';
import PromptDeckArchetype from './components/PromptDeckArchetype.jsx';

import PromptFlowSimpleChat from './components/PromptFlowSimpleChat.jsx';
import ArchetypeDecks from './components/ArchetypeDecks.jsx';
import ArchetypeCircles from './components/ArchetypeCircles.jsx';


import PromptFlowDashboard from './components/PromptFlowDashboard.jsx';

import TextInput from "./components/TextInput.jsx"
import TextInputColumns from "./components/TextInputColumns.jsx"
import ProfileManager from './components/ProfileManager.jsx';

import PersonalKV from './components/PersonalKV.jsx';

import Feed from "./components/DiscoveryFeed.jsx";
import DiscoveryFeedTopics from './components/DiscoveryFeedTopics.jsx';
import EditorComponent from "./components/EditorComponent.jsx"
import DiscoveryFeedCreator from './components/DiscoveryFeedCreator.jsx';

import DiscoveryFeed from './components/DiscoveryFeed2.jsx';
import DiscoverChat from "./components/ode/DiscoverChat.jsx";
import MirrorFlow from './components/MirrorFlow.jsx';

import SlackInterfaceTester from './components/SlackInterfaceTester.jsx';

const router = createBrowserRouter([
  {
    path: "/",
    element: <Login />,
  },
  {
    path: "/app",
    element: <Login />,
  },
  {
    path: "/app/circle-view",
    element: <CircleView />,
  },
  {
    path: "/app/prompt-view-category/:category",
    element: <PromptViewCategory />,
  },
  {
    path: "/app/prompt-view-category/:category/:subcategory",
    element: <PromptViewCategory />,
  },
  {
    path: "/app/prompt-flow-designer",
    element: <PromptFlowDesigner />,
  },
  {
    path: "/app/prompt-flow-designer/:promptFlowId",
    element: <PromptFlowDesigner />,
  },
  {
    path: "/app/prompt-flow-designer1",
    element: <PromptFlowDesigner1 />,
  },
  {
    path: "/app/prompt-flow-designer1/:promptFlowId",
    element: <PromptFlowDesigner1 />,
  },
  {
    path: "/app/login",
    element: <Login />,
  },
  {
    path: "/app/prompt-flow-chat/:promptFlowId",
    element: <PromptFlowChat />,
  },
  {
    path: "/app/wstest",
    element: <WebsocketTests />,
  },
  {
    path: "/app/prompt-lib-designer",
    element: <PromptLibDesigner />
  },
  {
    path: "/app/prompt-lib-designer/:promptLibId",
    element: <PromptLibDesigner />
  },
  {
    path: "/app/prompt-lib/:promptLibId",
    element: <PromptTemplate />
  },
  {
    path: "/app/folders",
    element: <FolderComponent />
  },
  {
    path: "/app/prompt-deck",
    element: <PromptDeck />
  },
  {
    path: "/app/prompt-deck-ui",
    element: <PromptDeckUI2 />
  },
  {
    path: "/app/prompt-deck-ui/:promptDeckId",
    element: <PromptDeckUI2 />
  },
  {
    path: "/app/prompt-deck-archetype",
    element: <PromptDeckArchetype />
  },
  {
    path: "/app/prompt-deck/:promptDeckId",
    element: <PromptDeckArchetype />
  },
  {
    path: "/app/prompt-chat/:promptFlowId",
    element: <PromptFlowSimpleChat />
  },
  {
    path: "/app/archetype-categories",
    element: <ArchetypeDecks />
  },
  {
    path: "/app/flower",
    element: <ArchetypeCircles />
  },
  {
    path: "/app/prompt-deck/:promptDeckId",
    element: <PromptDeckArchetype />
  },
  {
    path: "/app/dashboard",
    element: <Dashboard />
  },
  {
    path: "/app/flow-dashboard",
    element: <PromptFlowDashboard />
  },
  {
    path: "/app/text-input",
    element: <TextInput />
  },
  {
    path: "/app/text-input-columns",
    element: <TextInputColumns />
  },
  {
    path: "/app/profiles",
    element: <ProfileManager />
  },
  {
    path: "/app/personal-kv",
    element: <PersonalKV />
  },
  {
    path: "/app/discovery",
    element: <Feed />
  },
  {
    path: "/app/discovery/:discoveryFeedId",
    element: <DiscoveryFeed />
  },
  {
    path: "/app/editor",
    element: <EditorComponent />
  },
  {
    path: "/app/discovery-topics",
    element: <DiscoveryFeedTopics />
  },
  {
    path: "/app/discovery-feed-creator",
    element: <DiscoveryFeedCreator />
  },
  {
    path: "/app/discovery-feed-creator/:discoveryFeedId",
    element: <DiscoveryFeedCreator />
  },
  {
    path: "/app/ode/:discoveryFeedId",
    element: <DiscoverChat />
  },
  {
    path: "/app/mirror",
    element: <MirrorFlow />
  },
  {
    path: "/app/slack-interface-tester",
    element: <SlackInterfaceTester />
  }
]);

amplitude.init('502b3795c25c5c00393305866105dcba', {
  defaultTracking: true,
});

ReactDOM.createRoot(document.getElementById('root')).render(
  

  // <React.StrictMode>
    <RouterProvider router={router} />,
  // </React.StrictMode>,
)

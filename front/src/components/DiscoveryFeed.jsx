// App.js or Feed.js
import MediaItem from './MediaItem';
import InfiniteScroll from 'react-infinite-scroll-component';
import Api from './api';

import React, { useState, useEffect } from 'react';

const default_items = [
    {
      "id": 3,
      "id_source": 1,
      "kind": "article",
      "source_url": "https://lwn.net/SubscriberLink/951337/e9139cdb65a9cb93/",
      "title": "The real realtime preemption end game",
      "summary": "The addition of real-time support to Linux, which began in 2004, is nearing its end, according to Thomas Gleixner at the 2023 Linux Plumbers Conference. The real-time preemption project aims to ensure that the highest-priority process can always run with minimal delay. It has led to the rewriting of much of the core kernel, with benefits beyond real-time use. The last major issue to be addressed is with printk(), the function used to send messages to system consoles and logs. This function is currently fully synchronous, causing latency issues. Developers have been working on this problem since 2018, with three final patch sets currently in progress.\n",
      "image": "https://oaidalleapiprodscus.blob.core.windows.net/private/org-040KKyZUXOoPD0iUpOMoOSuy/user-vKVyY5s7B6EkM0c8ngCyo3tZ/img-d7l0u8E18nZPRagahaTCNomP.png?st=2023-11-16T19%3A46%3A26Z&se=2023-11-16T21%3A46%3A26Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-11-16T19%3A54%3A04Z&ske=2023-11-17T19%3A54%3A04Z&sks=b&skv=2021-08-06&sig=YoziZjUKE8I1h4iGhygaaJyvCh0SQ91vlcokwVj0wRk%3D",
      "payload": null,
      "created_on": "2023-11-16",
      "updated_on": "2023-11-16"
    },
    {
      "id": 5,
      "id_source": 1,
      "kind": "article",
      "source_url": "https://www.airplane.dev/blog/migrating-to-opentelemetry",
      "title": "Migrating to OpenTelemetry",
      "summary": "Airplane, a tech company, has migrated most of its observability data generation and collection to the OpenTelemetry (OTel) standard. The move has enabled the firm to collect data more reliably, connect more easily with different vendors and better monitor and control costs. OTel is a set of standards and tools for processing observability data, defining basic concepts and protocols for transmitting data from one system to another. It also provides a set of SDK libraries that allow for the instrumentation of applications in various programming languages and the pushing of data via the former protocols. Finally, it provides a collector, a centralized component that receives data from various sources, applies arbitrary transformations to it, and exports the data to one or more downstream destinations.",
      "image": "https://www.airplane.dev/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Fgradient-1-mobile.0cf6d4dd.png&w=1080&q=75",
      "payload": null,
      "created_on": "2023-11-16",
      "updated_on": "2023-11-16"
    }
  ];

function Feed() {
    
    const [items, setItems] = useState([]);
    const [hasMore, setHasMore] = useState(true);
    const [page, setPage] = useState(1);
    const api = new Api();

    // Function to fetch items
    const fetchItems = async (pageNum) => {
        try {
            const response = await api.getDiscoveryItems(pageNum);
            console.log(response);
            return response; 
        } catch (error) {
            console.error("Error fetching data:", error);
            return [];
        }
    };

    // Initial data load
    useEffect(() => {
        fetchItems(1).then(newItems => {
            setItems(newItems);
        });
    }, []);

    // Function to fetch more data
    const fetchMoreData = () => {
        const nextPage = page + 1;
        fetchItems(nextPage).then(newItems => {
            if (newItems.length === 0) {
                setHasMore(false);
            } else {
                setItems([...items, ...newItems]);
                setPage(nextPage);
            }
        });
    };

    const handleUpvote = (itemId) => {
        console.log("Upvoted:", itemId);
        // Implement upvote logic
    };

    const handleDownvote = (itemId) => {
        console.log("Downvoted:", itemId);
        // Implement downvote logic
    };

    const handleSave = (itemId) => {
        console.log("Saved:", itemId);
        // Implement save logic
    };

    const handleComment = (itemId) => {
        console.log("Comment on:", itemId);
        // Implement comment logic
    };


    return (
        <div className='container'
                
            >
            <div className='row'>
                <div className='col-sm-2'></div>
                <div className='col-sm-8'>
                    <InfiniteScroll
                        dataLength={items.length}
                        next={fetchMoreData}
                        hasMore={hasMore}
                        loader={<h4>Loading...</h4>}
                    >
                        {items.map(item => (
                                <MediaItem
                                    key={item.id}
                                    item={item}
                                    onUpvote={handleUpvote}
                                    onDownvote={handleDownvote}
                                    onSave={handleSave}
                                    onComment={handleComment}
                                />
                            ))}
                        
                    </InfiniteScroll>
                </div>
                <div className='col-sm-2'></div>
            </div>
        </div>

    );

}

export default Feed;

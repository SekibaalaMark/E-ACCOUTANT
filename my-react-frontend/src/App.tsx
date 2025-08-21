import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import ExampleComponent from './components/ExampleComponent';

const App: React.FC = () => {
    return (
        <Router>
            <div>
                <h1>My Django API Frontend</h1>
                <Switch>
                    <Route path="/" exact component={ExampleComponent} />
                    {/* Add more routes here as needed */}
                </Switch>
            </div>
        </Router>
    );
};

export default App;
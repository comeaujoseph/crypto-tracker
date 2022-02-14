
<div align="center">

# Crypto Tracker

Crypto Tracker is a tracker for cryptocurrency prices.

</div>

<!-- TABLE OF CONTENTS -->
<details>
<summary>Table of Contents</summary>
<ol>
  <li>
    <a href="#getting-started">Getting Started</a>
    <ul>
      <li><a href="#prerequisites">Prerequisites</a></li>
      <li><a href="#install-and-run">Install and Run</a></li>
      <li><a href="#usage">Usage</a></li>
    </ul>
  </li>
  <li><a href="#testing">Testing</a></li>
  <li><a href="#features">Features</a></li>
  <li>
    <a href="#production">Production (scalability)</a>
    <ul>
      <li><a href="#architecture">Architecture</a></li>
      <li><a href="#postgresql">PostgreSQL</a></li>
      <li><a href="#redis">Redis</a></li>
      <li><a href="#celery">Celery</a></li>
      <li><a href="#dashboard">Dashboard</a></li>
      <li><a href="#maintenance">Maintenance</a></li>
    </ul>
  </li>
  <li><a href="#questions">Questions</a></li>
</ol>
</details>

## Getting Started

### Prerequisites

An overview of the technology stack used for the take-home assignment:

- Python 3.9+ 
- [Django](https://www.djangoproject.com/): Python web framework
- [SQLite](https://www.sqlite.org/index.html): SQL Database

I started out using [Celery](https://docs.celeryproject.org/en/stable/), a Distributed Task Queue, to query the prices 
but after writing the application it felt a bit overkill for the purpose of the assignment. You would need to run multiple 
processes (celery worker, celery scheduler, and redis) or install docker. I switched to using a [scheduler](https://apscheduler.readthedocs.io/en/3.x/). 

### Install and Run

1. Create Python virtual environment

```bash
make venv
```

2. Install dependencies

```bash
make requirements
```

3. Setup SQLite database

```bash
make migrations && make fixtures
```

4. Run API

```bash
make server
```

6. Run Scheduler

```bash
make scheduler
```

### Usage

You can now open the API in your browser at `http://127.0.0.1:8000/api/v1` or click [here](http://localhost:8000/api/v1).
From the web browsable API you can view metrics, ranking, and historical data. You can also interact with the API using 
the command line tool `curl`.

List the metrics:

    $ curl -H 'Accept: application/json; indent=4' http://localhost:8000/api/v1/metrics
    [
        {
            "id": 1,
            "pair": "BTC/USD",
            "metric": "price"
        },
        {
            "id": 2,
            "pair": "LTC/USD",
            "metric": "price"
        }, ....
    ]

Get metric details:

    $ curl -H 'Accept: application/json; indent=4' http://localhost:8000/api/v1/metrics/1
    {
        "rank": 6,
        "id": 1,
        "pair": "BTC/USD",
        "metric": "price"
    }

List the metric historical data (24hrs):

    $ curl -H 'Accept: application/json; indent=4' http://localhost:8000/api/v1/metrics/1/records
    [
        {
            "timestamp": "2022-02-13T22:06:00.310744Z",
            "value": 42284.6
        },
        {
            "timestamp": "2022-02-13T22:09:00.358059Z",
            "value": 42251.6
        },
        {
            "timestamp": "2022-02-13T22:09:00.360800Z",
            "value": 42251.6
        },
        {
            "timestamp": "2022-02-13T22:10:00.169137Z",
            "value": 42252.1
        },....
    ]

## Testing

Run unit tests with:

```bash
make test
```

Additional Testing:
- Integration
- Performance
- Load
- Stress

Unit & Integration testing should be a part of the CI/CD.

Performance, load, and stress testing should be done ad hoc. Before going to production, these 3 types of testing should
be done to ensure that resources are provisioned correctly.

<!-- Features -->
## Features

- [x] RESTful API
- [x] Periodic Updates (1 minute)
  - [ ] Configurable intervals
- [x] Historical metrics (24 hours)
  - [ ] Dynamic range (query parameter)
  - [ ] Pagination
  - [ ] Caching
- [x] Metric Rank
- [x] Asynchronous Support
- [ ] Exchanges
  - [x] Configurable exchange (kraken)
  - [ ] Exchange switching
  - [ ] Add / Delete Pairs
- [ ] Dashboard
- [ ] Metric Alerts
- [ ] Authentication / Authorization

### Metric Alerts

**Request:** send an alert whenever a metric exceeds 3x the value of its average in the last 1 hour

**Proposal:**

* User selects a metric(s) to monitor (e.g. BTC/USD) 
* User configures a channel(s) for the alert (e.g. Slack)
* No noisy alerts! Alert will be sent only once for a given time window

A Celery task will be triggered whenever the metric data has been updated. The task will first check to see 
if when last the alert was sent. If no alert or alert expired, check to see if the metric has exceeded the 
1-hour average by 3x. If YES, send alert.

## Production

Documentation on how to make production ready and scalable.

### Architecture

A high-level overview of the architectural design:

1. Dashboard (React.js)
2. API (Django) 
   1. Requests
   2. Task creation
3. Broker (Redis)
   1. Celery broker responsible to delivering tasks to workers
4. Workers (Celery)
   1. Worker "nodes" process tasks from the queue (fetching cryptocurrency prices) and store the results in the database
5. Database (PostgreSQL)
   1. Tracked metrics
   2. Metric records (prices)
6. Cache (Redis)

The application will be run on AWS EKS, Amazon Elastic Kubernetes Service. Kubernetes cluster creation and management will
be done via [eksctl](https://eksctl.io). Application management via [Helm](https://helm.sh/).

Tooling:
- eksctl
- Helm
- Docker

Our infrastructure can be scaled vertically and/or horizontally. **Vertically scaling** is done by creating a new 
k8s nodegroup with a higher EC2 instance type. For **horizontal scaling** we have two options:

- Cluster Autoscaler: utilizes Amazon EC2 Auto Scaling Groups to manage node groups
- Horizontal Pod Autoscaling: as load increases it will deploy more pods (application)

The application is separated into 2 component; API and worker, so that we can scale and rollout releases independently.
The API will use Gunicorn, which is a pure-Python WSGI server for UNIX, and a AWS classic load balancer 
to distribute traffic.

**Note:** CI/CD (Jenkins + BlueOcean) not documented. 

### PostgreSQL

PostgreSQL (AWS RDS) to store tracked metrics and historical data. AWS RDS supports vertical and horizontal scaling:
increase instance size, replicas (multi-region support too), partitioning. RDS provides backup and restore functionality.

### Redis

Redis will be used for distributing tasks to the Celery workers and API caching. AWS ElasticCache 
(managed redis solution) supports cluster mode, backups, and restores. Redis clustering will provide scalability via:
auto-scaling, sharding, and replication.

### Celery

Celery will allow use to process task asynchronously and distributed. Celery workers can be scaled based on the number
of tasks in the queue and independently of API.

### Dashboard

The dashboard will be written in React.js and hosted on a CDN.

### Maintenance

Monitoring / Alerting / Tracing

#### Prometheus & Grafana

Prometheus to monitor our K8s resources. Grafana to visualize and alert on the metrics. Alerts sent to Slack and/or 
PagerDuty depending on severity.

#### Application logs

An ELK stack (elasticsearch, kibana, filebeat, and logstash) used for application logs. Grafana 
to visualize and alerts on application metrics.

#### Alerting Platforms

- Slack
- PagerDuty

#### Jaeger

End-to-end distributed tracing.

#### Celery Flower

Flower is a web based tool for monitoring and administrating Celery clusters

## Questions

Questions are answered throughout the README, but I provided a brief summary below.

1. What would you change if you needed to track many metrics? 
    
    Split up the periodic task into a task per metric or group of metrics. 
    
2. What if you needed to sample them more frequently? 

    If you don't have to worry about rate-limiting, Python Celery would allow scheduling jobs with a shorter interval.

3. What if you had many users accessing your dashboard to view metrics?

    Caching [Redis](#redis) + Scalability [Production](#production)

4. How would you extend testing for an application of this kind (beyond what you implemented)? [Answer](#testing)
5. Feature request proposal [Answer](#metric-alerts)
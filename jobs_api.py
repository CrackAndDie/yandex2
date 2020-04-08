import flask
from flask import jsonify, request
from data import db_session
from data.jobs import Jobs
from data.category import Category


blueprint = flask.Blueprint('jobs_api', __name__,
                            template_folder='templates')


@blueprint.route('/api/jobs')
def get_jobs():
    session = db_session.create_session()
    jobs = session.query(Jobs).all()
    return jsonify({'jobs': [item.to_dict(only=('job', 'team_leader',
                                                'work_size', 'collaborators',
                                                'is_finished', 'categories.id'))
                             for item in jobs]})


@blueprint.route('/api/jobs/<int:jobs_id>',  methods=['GET'])
def get_one_jobs(jobs_id):
    session = db_session.create_session()
    jobs = session.query(Jobs).get(jobs_id)
    if not jobs:
        return jsonify({'error': 'Not found'})
    return jsonify({'jobs': jobs.to_dict(only=('job', 'team_leader',
                                               'work_size', 'collaborators',
                                               'is_finished', 'categories.id'))})


@blueprint.route('/api/jobs', methods=['POST'])
def create_jobs():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['id', 'job', 'team_leader', 'work_size', 'collaborators', 'is_finished', 'categories']):
        return jsonify({'error': 'Bad request'})
    session = db_session.create_session()
    jobs = session.query(Jobs).filter(Jobs.id == request.json['id']).first()
    if not jobs:
        jobs = Jobs()
        jobs.job = request.json['job']
        jobs.id = request.json['id']
        jobs.team_leader = request.json['team_leader']
        jobs.work_size = request.json['work_size']
        jobs.collaborators = request.json['collaborators']
        jobs.is_finished = request.json['is_finished']
        cate = session.query(Category).filter(Category.name == request.json['categories']).first()
        if cate:
            if len(jobs.categories) == 0:
                jobs.categories.append(cate)
            else:
                jobs.categories[0] = cate
        else:
            cate = Category()
            cate.name = request.json['categories']
            session.add(cate)
            if len(jobs.categories) == 0:
                jobs.categories.append(cate)
            else:
                jobs.categories[0] = cate
        session.add(jobs)
        session.commit()
        return jsonify({'success': 'OK'})
    else:
        return jsonify({'error': 'Id already exists'})


@blueprint.route('/api/jobs/<int:jobs_id>', methods=['DELETE'])
def delete_jobs(jobs_id):
    session = db_session.create_session()
    jobs = session.query(Jobs).get(jobs_id)
    if not jobs:
        return jsonify({'error': 'Not found'})
    session.delete(jobs)
    session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/jobs', methods=['PUT'])
def edit_jobs():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif 'id' not in request.json:
        return jsonify({'error': 'There is no ID'})
    session = db_session.create_session()
    jobs = session.query(Jobs).filter(Jobs.id == request.json['id']).first()
    if jobs:
        jobs.job = request.json.get('job', jobs.job)
        jobs.team_leader = request.json.get('team_leader', jobs.team_leader)
        jobs.work_size = request.json.get('work_size', jobs.work_size)
        jobs.collaborators = request.json.get('collaborators', jobs.collaborators)
        jobs.is_finished = request.json.get('is_finished', jobs.is_finished)
        if 'categories' in request.json:
            cate = session.query(Category).filter(Category.name == request.json['categories']).first()
            if cate:
                if len(jobs.categories) == 0:
                    jobs.categories.append(cate)
                else:
                    jobs.categories[0] = cate
            else:
                cate = Category()
                cate.name = request.json['categories']
                session.add(cate)
                if len(jobs.categories) == 0:
                    jobs.categories.append(cate)
                else:
                    jobs.categories[0] = cate
        session.add(jobs)
        session.commit()
        return jsonify({'success': 'OK'})
    else:
        return jsonify({'error': 'There is no element with the id'})

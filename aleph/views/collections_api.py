from flask import Blueprint, request
from apikit import obj_or_404, jsonify, request_data
from normality import ascii_text

from aleph.core import USER_QUEUE, USER_ROUTING_KEY, db
from aleph.model import Collection
from aleph.search import QueryState, lead_count, collections_query
from aleph.events import log_event
from aleph.logic import delete_collection, update_collection
from aleph.logic import analyze_collection

blueprint = Blueprint('collections_api', __name__)


@blueprint.route('/api/1/collections', methods=['GET'])
def index():
    state = QueryState(request.args, request.authz)
    result = collections_query(state)
    return jsonify(result)


@blueprint.route('/api/1/collections', methods=['POST', 'PUT'])
def create():
    request.authz.require(request.authz.logged_in)
    data = request_data()
    data['managed'] = False
    collection = Collection.create(data, request.authz.role)
    db.session.commit()
    update_collection(collection)
    log_event(request)
    return jsonify(collection)


@blueprint.route('/api/1/collections/<int:id>', methods=['GET'])
def view(id):
    collection = obj_or_404(Collection.by_id(id))
    request.authz.require(request.authz.collection_read(collection))
    data = collection.to_dict()
    data['lead_count'] = lead_count(id)
    return jsonify(data)


@blueprint.route('/api/1/collections/<int:id>', methods=['POST', 'PUT'])
def update(id):
    collection = obj_or_404(Collection.by_id(id))
    request.authz.require(request.authz.collection_write(collection))
    collection.update(request_data())
    db.session.add(collection)
    db.session.commit()
    update_collection(collection)
    log_event(request)
    return view(id)


@blueprint.route('/api/1/collections/<int:id>/process',
                 methods=['POST', 'PUT'])
def process(id):
    collection = obj_or_404(Collection.by_id(id))
    request.authz.require(request.authz.collection_write(collection))
    analyze_collection.apply_async([collection.id], queue=USER_QUEUE,
                                   routing_key=USER_ROUTING_KEY)
    log_event(request)
    return jsonify({'status': 'ok'})


@blueprint.route('/api/1/collections/<int:id>/pending', methods=['GET'])
def pending(id):
    collection = obj_or_404(Collection.by_id(id))
    request.authz.require(request.authz.collection_read(collection))
    q = collection.pending_entities()
    q = q.limit(30)
    entities = []
    for entity in q.all():
        data = entity.to_dict()
        data['name_latin'] = ascii_text(entity.name)
        entities.append(data)
    return jsonify({'results': entities, 'total': len(entities)})


@blueprint.route('/api/1/collections/<int:id>', methods=['DELETE'])
def delete(id):
    collection = obj_or_404(Collection.by_id(id))
    request.authz.require(request.authz.collection_write(collection))
    delete_collection.apply_async([collection.id],
                                  queue=USER_QUEUE,
                                  routing_key=USER_ROUTING_KEY)
    log_event(request)
    return jsonify({'status': 'ok'})

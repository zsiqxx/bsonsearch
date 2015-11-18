import bson
import ctypes
from hashlib import md5


#dropped by libbsoncompare rpm.
# Install this from pkgs.bauman.in to get dep tree
LIBRARY_LOC="/usr/lib64/libbsoncompare.so"



class bsoncompare:
    def __init__(self):
        self.bc = ctypes.CDLL(LIBRARY_LOC)
        self.matchers = {} #keys = string, value = c-pointers
        self.docs = {} #keys = string, value = c-pointers

    def destroy_matcher(self, matcher_id):
        if isinstance(matcher_id, list) or isinstance(matcher_id, dict):
            matcher_ids = [matcher_id_ for matcher_id_ in matcher_id]
            [self.destroy_matcher(matcher_ids_) for matcher_ids_ in matcher_ids]
        elif isinstance(matcher_id, basestring):
            if matcher_id not in self.matchers:
                return True #let caller believe it's been deleted.
            if matcher_id in self.matchers:
                self.bc.matcher_destroy(self.matchers[matcher_id])
                del(self.matchers[matcher_id])

    def generate_matcher(self, spec):
        if isinstance(spec, dict):
            encoded_spec = bson.BSON.encode(spec)
        elif isinstance(spec, basestring):
            encoded_spec = spec
        else:
            raise ValueError
        matcher_id = md5(encoded_spec).hexdigest()
        if matcher_id not in self.matchers:
            self.matchers[matcher_id] = self.bc.generate_matcher(encoded_spec,
                                                                 len(encoded_spec))
        return matcher_id



    def destroy_doc(self, doc_id):
        if isinstance(doc_id, list) or isinstance(doc_id, dict):
            doc_ids = [doc_id_ for doc_id_ in doc_id]
            [self.destroy_doc(doc_ids_) for doc_ids_ in doc_ids]
        elif isinstance(doc_id, basestring):
            if doc_id not in self.docs:
                return True
            if doc_id in self.docs:
                self.bc.doc_destroy(self.docs[doc_id])
                del(self.docs[doc_id])


    def generate_doc(self, doc):
        if isinstance(doc, dict):
            encoded_doc = bson.BSON.encode(doc)
        elif isinstance(doc, basestring):
            encoded_doc = doc
        else:
            raise ValueError
        doc_id = md5(encoded_doc).hexdigest()
        if doc_id not in self.docs:
            self.docs[doc_id] = self.bc.generate_doc(encoded_doc,
                                                     len(encoded_doc))
        return doc_id


    def match_doc(self, matcher_id, doc_id):
        matcher  = self.matchers[matcher_id] #pointer
        document = self.docs[doc_id] #pointer
        ismatch = self.bc.matcher_compare_doc(matcher, document)
        return bool(ismatch)


    def match(self, matcher_id, document):
        if isinstance(matcher_id, dict):
            matcher_id = self.generate_matcher(matcher_id)
        matcher = self.matchers[matcher_id]
        if isinstance(document, dict):
            encoded_document = bson.BSON.encode(document)
        elif isinstance(document, basestring):
            encoded_document = document
        else:
            raise ValueError
        ismatch = self.bc.matcher_compare(matcher,
                                          encoded_document,
                                          len(encoded_document))
        return bool(ismatch)


    def explode_namespace(self, prefix_len, namespace, doc_id):
        try:
            document = self.docs[doc_id]
        except KeyError:
            raise KeyError("destroy_doc was already called on document")
        curpos = prefix_len
        curpos = namespace.find(".",curpos+1)
        if curpos > 0:
            at_end = False
            current_ns = namespace[:curpos]
        else:
            at_end=True
            current_ns =  namespace
        array_len = self.bc.get_array_len(document, current_ns, len(current_ns))
        if at_end and not array_len:
            yield current_ns
        elif not at_end and not array_len:
            next_ns_prefix = "%s" %(current_ns)
            next_ns = "%s%s" %(next_ns_prefix, namespace[curpos:])
            for yield_ns in self.explode_namespace(len(next_ns_prefix), next_ns, doc_id):
                yield yield_ns
        for x in xrange(array_len):
            next_ns_prefix = "%s.%s" %(current_ns,x)
            if at_end:
                next_ns = "%s%s" %(next_ns_prefix, "")
            else:
                next_ns = "%s%s" %(next_ns_prefix, namespace[curpos:])
            for yield_ns in self.explode_namespace(len(next_ns_prefix), next_ns, doc_id):
                yield yield_ns
        return

    def convert_to_or(self, ns_list, value):
        query_list = []
        for ns in ns_list:
            query_list.append({ns:value})
        if query_list:
            query = { "$or": query_list }
        else:
            query = None
        return query

    def convert_to_and(self, spec, doc_id):
        and_list = []
        query = {"$and":and_list}
        for key, value in spec.items():
            ns_list = [x for x in self.explode_namespace(0, key, doc_id)]
            query_or = self.convert_to_or(ns_list, value)
            if query_or:
                and_list.append(query_or)
        if not and_list:
            query=None
        return query
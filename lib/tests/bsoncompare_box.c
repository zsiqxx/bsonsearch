#include <stdio.h>
#include <bsoncompare.h>

int compare_json(const char *json,
                 const char *jsonspec ){
    bson_error_t error;
    bson_error_t error2;
    bson_t      *spec;
    bson_t      *doc;
    doc = bson_new_from_json (json, -1, &error);
    spec = bson_new_from_json (jsonspec, -1, &error2);
    const uint8_t *spec_bson = bson_get_data(spec);
    const uint8_t *doc_bson = bson_get_data(doc);
    int yes = compare(spec_bson, spec->len, doc_bson, doc->len);
    bson_free(spec);
    bson_free(doc);
    return yes;
}


int
main (int   argc,
      char *argv[])
{

    BSON_ASSERT(compare_json("{\"loc\": [1,1]}",
                             "{\"loc\": { \"$geoWithin\": { \"$polygon\": [ [ 1 , 1 ], [ 3 , 6 ], [ 6 , 0 ] ] } } }"));

    BSON_ASSERT(compare_json("{\"loc\": [2,3]}",
                             "{\"loc\": { \"$geoWithin\": { \"$polygon\": [ [ 1 , 1 ], [ 3 , 6 ], [ 6 , 0 ] ] } } }"));

    BSON_ASSERT(!compare_json("{\"loc\": [20,3]}",
                             "{\"loc\": { \"$geoWithin\": { \"$polygon\": [ [ 1 , 1 ], [ 3 , 6 ], [ 6 , 0 ] ] } } }"));

    BSON_ASSERT(compare_json("{\"loc\": [0,3]}",
                             "{\"loc\": { \"$geoWithin\": { \"$box\":  [ [ 0, 0 ], [ 100, 101 ] ] } } }"));
    BSON_ASSERT(compare_json("{\"loc\": [3,0]}",
                             "{\"loc\": { \"$geoWithin\": { \"$box\":  [ [ 0, 0 ], [ 100, 100 ] ] } } }"));
    BSON_ASSERT(compare_json("{\"loc\": [100,0]}",
                             "{\"loc\": { \"$geoWithin\": { \"$box\":  [ [ 0, 0 ], [ 100, 100 ] ] } } }"));
    BSON_ASSERT(compare_json("{\"loc\": [0,100]}",
                             "{\"loc\": { \"$geoWithin\": { \"$box\":  [ [ 0, 0 ], [ 100, 100 ] ] } } }"));
    BSON_ASSERT(!compare_json("{\"loc\": [-1,100]}",
                             "{\"loc\": { \"$geoWithin\": { \"$box\":  [ [ 0, 0 ], [ 100, 100 ] ] } } }"));
    BSON_ASSERT(!compare_json("{\"loc\": [2,101]}",
                              "{\"loc\": { \"$geoWithin\": { \"$box\":  [ [ 0, 0 ], [ 100, 100 ] ] } } }"));

    return 0;
}
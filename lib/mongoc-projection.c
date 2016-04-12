/*
 * Copyright (c) 2016 Bauman
 * The MIT License (MIT)
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */
#ifdef WITH_PROJECTION
#include "mongoc-matcher.h"
#include "mongoc-matcher-private.h"
#include "mongoc-matcher-op-private.h"
#include "mongoc-projection.h"
#include "mongoc-bson-descendants.h"


/*
 *--------------------------------------------------------------------------
 *
 * _mongoc_matcher_parse_projection --
 *
 *       Parse an aggregation spec containing a projection operator
 *       $project.
 *
 *       See the following link for more information.
 *
 *       https://docs.mongodb.org/manual/tutorial/project-fields-from-query-results/
 *
 *       Differences, this does not support the 0 value to omit a single field.
 *       If the key is present, it will do it's best to include it in the output
 *
 *
 * Requires:
 *       iter MUST Be a document type, otherwise, outcome undefined.
 *
 * Returns:
 *       A newly allocated mongoc_matcher_op_t if successful; otherwise
 *       NULL and @error may be set.
 *
 * Side effects:
 *       @error may be set.
 *
 *--------------------------------------------------------------------------
 */
mongoc_matcher_op_t *
_mongoc_matcher_parse_projection (mongoc_matcher_opcode_t  opcode,  /* IN */
                                  bson_iter_t             *iter,    /* IN */
                                  bool                     is_root, /* IN */
                                  bson_error_t            *error)   /* OUT */
{
    mongoc_matcher_op_t *op = NULL;
    mongoc_matcher_op_t *left_op = NULL;
    BSON_ASSERT (opcode == MONGOC_MATCHER_OPCODE_PROJECTION);
    BSON_ASSERT (iter);

    bson_iter_t child;
    if (bson_iter_recurse(iter, &child)) {
        op = _mongoc_matcher_parse_projection_loop(&child, error);
    }
    return op;
}
mongoc_matcher_op_t *
_mongoc_matcher_parse_projection_loop (bson_iter_t             *iter,    /* IN */
                                       bson_error_t            *error)   /* OUT */
{
    mongoc_matcher_op_t *on_the_left=NULL;
    mongoc_matcher_op_t *next_left = NULL;
    if (bson_iter_next(iter)){
        const bson_value_t * value = bson_iter_value(iter);
        switch (value->value_type){
            case BSON_TYPE_BINARY:
            case BSON_TYPE_INT32:
            {
                const char * key = bson_iter_key (iter);
                next_left = _mongoc_matcher_parse_projection_loop(iter, error);
                on_the_left = (mongoc_matcher_op_t *)bson_malloc0 (sizeof *on_the_left);
                on_the_left->base.opcode = MONGOC_MATCHER_OPCODE_PROJECTION;
                on_the_left->projection.path = bson_strdup(key);
                on_the_left->projection.next = next_left;
                break;
            }
            default:
                break;
        }
    }
    return on_the_left;

}

bool
mongoc_matcher_projection_execute(mongoc_matcher_op_t *op,     //in
                                  bson_t              *bson,        //in
                                  bson_t              *projected)   //out
{
    assert(op->base.opcode == MONGOC_MATCHER_OPCODE_PROJECTION);
    /*
    bson_iter_t *iter;
    int checked = 0, skip=0;
    while (bson_iter_init (&iter, bson) &&
           bson_iter_find_descendants (iter, op->projection.path, &skip, &iter)){

        skip = ++checked;
    }
    */
    return false;
}

#endif //WITH_PROJECTION
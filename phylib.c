#include "phylib.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>

phylib_object *phylib_new_still_ball( unsigned char number, phylib_coord *pos ) {
    
    // allocate memory and check if dynamic memory allocation was successful
    phylib_object *stillObject = malloc(sizeof(phylib_object));
    
    if (stillObject == NULL) {
        return NULL; 
    }

    stillObject->type = PHYLIB_STILL_BALL;

    // transfer the information into the structure
    stillObject->obj.still_ball.number = number;
    stillObject->obj.still_ball.pos.x = pos->x;
    stillObject->obj.still_ball.pos.y = pos->y;

    return stillObject;
}

phylib_object *phylib_new_rolling_ball( unsigned char number, phylib_coord *pos, phylib_coord *vel, phylib_coord *acc ) {
    
    // allocate memory and check if dynamic memory allocation was successful
    phylib_object *rollingObject = malloc(sizeof(phylib_object));
    
    if (rollingObject == NULL) {
        return NULL; 
    }

    rollingObject->type = PHYLIB_ROLLING_BALL;

    // transfer the information into the structure
    rollingObject->obj.rolling_ball.number = number;
    rollingObject->obj.rolling_ball.pos.x = pos->x;
    rollingObject->obj.rolling_ball.pos.y = pos->y;

    rollingObject->obj.rolling_ball.vel.x = vel->x;
    rollingObject->obj.rolling_ball.vel.y = vel->y;

    rollingObject->obj.rolling_ball.acc.x = acc->x;
    rollingObject->obj.rolling_ball.acc.y = acc->y;

    return rollingObject;
}

phylib_object *phylib_new_hole( phylib_coord *pos ) {

    // allocate memory and check if dynamic memory allocation was successful
    phylib_object *holeObject = malloc(sizeof(phylib_object));
    
    if (holeObject == NULL) {
        return NULL; 
    }

    holeObject->type = PHYLIB_HOLE;

    // transfer the information into the structure
    holeObject->obj.hole.pos.x = pos->x;
    holeObject->obj.hole.pos.y = pos->y;

    return holeObject;

}

phylib_object *phylib_new_hcushion( double y ) {

    // allocate memory and check if dynamic memory allocation was successful
    phylib_object *hCushionObject = malloc(sizeof(phylib_object));
    
    if (hCushionObject == NULL) {
        return NULL; 
    }

    hCushionObject->type = PHYLIB_HCUSHION;

    // transfer the information into the structure
    hCushionObject->obj.hcushion.y = y;

    return hCushionObject;
}

phylib_object *phylib_new_vcushion( double x ) {

    // allocate memory and check if dynamic memory allocation was successful
    phylib_object *vCushionObject = malloc(sizeof(phylib_object));
    
    if (vCushionObject == NULL) {
        return NULL; 
    }

    vCushionObject->type = PHYLIB_VCUSHION;

    // transfer the information into the structure
    vCushionObject->obj.vcushion.x = x;

    return vCushionObject;
}

phylib_table *phylib_new_table( void ) {

    // allocate memory and check if dynamic memory allocation was successful
    phylib_table *table = malloc(sizeof(phylib_table));

    if (table == NULL) {
        return NULL;
    }

    table->time = 0.0;

    table->object[0] = phylib_new_hcushion(0.0); // top side horizontal cushion
    table->object[1] = phylib_new_hcushion(PHYLIB_TABLE_LENGTH); // bottom side horizontal cushion
    table->object[2] = phylib_new_vcushion(0.0); // left side vertical cushion
    table->object[3] = phylib_new_vcushion(PHYLIB_TABLE_WIDTH); // right side vertical cushion

    // create holes at the four corners
    phylib_coord pos;
    pos.x = 0.0; 
    pos.y = 0.0;

    table->object[4] = phylib_new_hole(&pos); // top left hole

    pos.x = 0.0; 
    pos.y = PHYLIB_TABLE_WIDTH; 
    table->object[5] = phylib_new_hole(&pos); // middle left hole

    pos.x = 0.0; 
    pos.y = PHYLIB_TABLE_LENGTH; 
    table->object[6] = phylib_new_hole(&pos); // bottom left hole

    pos.x = PHYLIB_TABLE_WIDTH; 
    pos.y = 0.0;
    table->object[7] = phylib_new_hole(&pos); // top right hole

    // create holes midway between the top holes and bottom holes
    pos.x = PHYLIB_TABLE_WIDTH; 
    pos.y = PHYLIB_TABLE_WIDTH;
    table->object[8] = phylib_new_hole(&pos); // middle right hole

    pos.x = PHYLIB_TABLE_WIDTH; 
    pos.y = PHYLIB_TABLE_LENGTH;
    table->object[9] = phylib_new_hole(&pos); // bottom right hole

    // set the remaining pointers to NULL -> 15 object balls and 1 cue ball
    for (int i = 10; i < PHYLIB_MAX_OBJECTS; i++) {
        table->object[i] = NULL;
    }

    return table;
}

void phylib_copy_object( phylib_object **dest, phylib_object **src ) {

    // check if src points to a location containing a NULL pointer
    if (*src == NULL) {
        *dest = NULL;
        return;
    }

    // allocate space for a new phylib_object
    *dest = malloc(sizeof(phylib_object));

    if (*dest == NULL) {
        return;
    }

    // copy over the contents of the object from the location pointed to by src
    memcpy(*dest, *src, sizeof(phylib_object));
}

phylib_table *phylib_copy_table( phylib_table *table ) {
    
    // allocate space for a new table
    phylib_table * newTable;
    newTable = malloc(sizeof(phylib_table));

    if (newTable == NULL) {
        return NULL;
    }

    // copy the contents of the existing table to the new table and return a pointer to the new table
    // memcpy(newTable, table, sizeof(phylib_table));

    // copy the time
    newTable->time = table->time;

    // copy each object
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        phylib_copy_object(&(newTable->object[i]), &(table->object[i]));
    }
    
    return newTable;
}

void phylib_add_object( phylib_table *table, phylib_object *object ) {

    // iterate over every object in the table array and if any object has a value == NULL
    // then assign the pointer to the address of the object
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        if (table->object[i] == NULL) {
            table->object[i] = object;
            return;
        }
    }
}

void phylib_free_table( phylib_table *table ) {
    
    // iterate over every object in the table array
    // if any object has a value other than NULL then free it
    if (table != NULL) {
        for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
            if (table->object[i] != NULL) {
                free(table->object[i]);
                table->object[i] = NULL;
            }
        }
    }
    free(table);
    table = NULL;
}

phylib_coord phylib_sub( phylib_coord c1, phylib_coord c2 ) {

    phylib_coord coordDiff;

    // subtract the x and y values of c2 from c1
    coordDiff.x = c1.x - c2.x;
    coordDiff.y = c1.y - c2.y;

    return coordDiff;
}

double phylib_length( phylib_coord c ) {

    // calculate the vector length
    double vectorLen; 
    vectorLen = sqrt((c.x * c.x) + (c.y * c.y));

    return vectorLen;
}

double phylib_dot_product( phylib_coord a, phylib_coord b ) {
    
    // calculate the dot product
    double dotProduct;
    dotProduct = ((a.x * b.x) + (a.y * b.y));

    return dotProduct;
}

double phylib_distance( phylib_object *obj1, phylib_object *obj2 ) {
    
    if (obj1->type != PHYLIB_ROLLING_BALL) {
        return (-1.0);
    }

    phylib_coord posDiff;

    if (obj2->type == PHYLIB_STILL_BALL) {

        // calculate the difference in position between the two balls
        // then using the difference in position calc the distance between the two balls
        posDiff = phylib_sub(obj1->obj.rolling_ball.pos, obj2->obj.still_ball.pos);
        double objDistance = (phylib_length(posDiff) - PHYLIB_BALL_DIAMETER);

        return objDistance;

    } else if (obj2->type == PHYLIB_ROLLING_BALL) {

        // calculate the difference in position between the two balls
        // then using the difference in position calc the distance between the two balls
        posDiff = phylib_sub(obj1->obj.rolling_ball.pos, obj2->obj.rolling_ball.pos);
        double objDistance = (phylib_length(posDiff) - PHYLIB_BALL_DIAMETER);

        return objDistance;
        
    } else if (obj2->type == PHYLIB_HOLE) {

        // calculate the difference in position between the ball and the hole
        // then using the difference in position calc the distance between the ball + hole
        posDiff = phylib_sub(obj1->obj.rolling_ball.pos, obj2->obj.hole.pos);
        double objDistance = (phylib_length(posDiff) - PHYLIB_HOLE_RADIUS);

        return objDistance;

    } else if (obj2->type == PHYLIB_VCUSHION) {

        // calculate the absolute difference in x coord between the ball and the vertical cushion
        // y-value is not considered since the y-value does not affect the distance from the vertical cushion
        posDiff.x = fabs(obj1->obj.rolling_ball.pos.x - obj2->obj.vcushion.x);
        posDiff.y = 0.0;

        double objDistance = (phylib_length(posDiff) - PHYLIB_BALL_RADIUS);
        return objDistance;

    } else if (obj2->type == PHYLIB_HCUSHION) {

        // calculate the absolute difference in y coord between the ball and the horizontal cushion
        // x-value is not considered since the x-value does not affect the distance from the horizontal cushion
        posDiff.y = fabs(obj1->obj.rolling_ball.pos.y - obj2->obj.hcushion.y);
        posDiff.x = 0.0;

        double objDistance = (phylib_length(posDiff) - PHYLIB_BALL_RADIUS);
        return objDistance;

    } else {
        return -1.0;
    }
}

void phylib_roll( phylib_object *new, phylib_object *old, double time ) {

    if (new->type != PHYLIB_ROLLING_BALL && old->type != PHYLIB_ROLLING_BALL) {
        return;
    }

    // update the position and velocity of the new ball
    new->obj.rolling_ball.pos.x = old->obj.rolling_ball.pos.x + (old->obj.rolling_ball.vel.x * time) + 0.5 * (old->obj.rolling_ball.acc.x * time * time);
    new->obj.rolling_ball.pos.y = old->obj.rolling_ball.pos.y + (old->obj.rolling_ball.vel.y * time) + 0.5 * (old->obj.rolling_ball.acc.y * time * time);

    new->obj.rolling_ball.vel.x = old->obj.rolling_ball.vel.x + (old->obj.rolling_ball.acc.x * time);
    new->obj.rolling_ball.vel.y = old->obj.rolling_ball.vel.y + (old->obj.rolling_ball.acc.y * time);

    // if the velocity changes sign, set the velocity and its corresponding acceleration to zero
    if ((old->obj.rolling_ball.vel.x * new->obj.rolling_ball.vel.x) < 0) {
        new->obj.rolling_ball.vel.x = 0.0;
        new->obj.rolling_ball.acc.x = 0.0;

    } 
    
    if ((old->obj.rolling_ball.vel.y * new->obj.rolling_ball.vel.y) < 0) {
        new->obj.rolling_ball.vel.y = 0.0;
        new->obj.rolling_ball.acc.y = 0.0;
    }
}

unsigned char phylib_stopped( phylib_object *object ) {

    // calculate the speed of the ball
    double objSpeed;
    objSpeed = phylib_length(object->obj.rolling_ball.vel);

    // if the ball speed is slower than PHYLIB_VEL_EPSILON then set the ball to still and transfer the number and position
    if (objSpeed < PHYLIB_VEL_EPSILON) {
 
        object->type = PHYLIB_STILL_BALL;
        object->obj.still_ball.number = object->obj.rolling_ball.number;
        object->obj.still_ball.pos = object->obj.rolling_ball.pos;

        return 1;
    }
    return 0;
}

void phylib_bounce( phylib_object **a, phylib_object **b ) {

    // double check that object a is a rolling ball
    if ((*a)->type != PHYLIB_ROLLING_BALL) {
        return;
    }

    // if object b is a horizontal cushion, reverse the y velocity and y acceleration of a
    if ((*b)->type == PHYLIB_HCUSHION) {
        
        (*a)->obj.rolling_ball.vel.y = -(*a)->obj.rolling_ball.vel.y;
        (*a)->obj.rolling_ball.acc.y = -(*a)->obj.rolling_ball.acc.y;

    // if object b is a vertical cushion, reverse the x velocity and x acceleration of a
    } else if ((*b)->type == PHYLIB_VCUSHION) {
        
        (*a)->obj.rolling_ball.vel.x = -(*a)->obj.rolling_ball.vel.x;
        (*a)->obj.rolling_ball.acc.x = -(*a)->obj.rolling_ball.acc.x;

    // if object b is a hole, free the memory of a and set it equal to NULL
    } else if ((*b)->type == PHYLIB_HOLE) {
        
        free(*a);
        *a = NULL;

    // if object b is a PHYLIB_STILL_BALL then change its type to PHYLIB_ROLLING_BALL
    } else if ((*b)->type == PHYLIB_STILL_BALL) {
        
        (*b)->type = PHYLIB_ROLLING_BALL;

        (*b)->obj.rolling_ball.number = (*b)->obj.still_ball.number;
        (*b)->obj.rolling_ball.pos.x = (*b)->obj.still_ball.pos.x;
        (*b)->obj.rolling_ball.pos.y = (*b)->obj.still_ball.pos.y;

        (*b)->obj.rolling_ball.vel.x = 0.0;
        (*b)->obj.rolling_ball.vel.y = 0.0;

        (*b)->obj.rolling_ball.acc.x = 0.0;
        (*b)->obj.rolling_ball.acc.y = 0.0;
    } 

    if ((*b)->type == PHYLIB_ROLLING_BALL) {
        
        // determine the difference in position between both objects (a-b)
        phylib_coord r_ab = phylib_sub((*a)->obj.rolling_ball.pos, (*b)->obj.rolling_ball.pos);

        // determine the relative velocity of a with respect to b (b-a)
        phylib_coord v_rel = phylib_sub((*a)->obj.rolling_ball.vel, (*b)->obj.rolling_ball.vel);

        double r_ab_len = phylib_length(r_ab);

        // create a normal vector and determine its x and y components
        phylib_coord n;
        n.x = (r_ab.x / r_ab_len);
        n.y = (r_ab.y / r_ab_len);

        double v_rel_n = phylib_dot_product(v_rel, n);

        // update the x and y components of velocity for both ball a and b
        (*a)->obj.rolling_ball.vel.x = (*a)->obj.rolling_ball.vel.x - (v_rel_n * n.x);
        (*a)->obj.rolling_ball.vel.y = (*a)->obj.rolling_ball.vel.y - (v_rel_n * n.y);
        (*b)->obj.rolling_ball.vel.x = (*b)->obj.rolling_ball.vel.x + (v_rel_n * n.x);
        (*b)->obj.rolling_ball.vel.y = (*b)->obj.rolling_ball.vel.y + (v_rel_n * n.y);

        // calculate the speed of a and b
        double aBallSpeed = phylib_length((*a)->obj.rolling_ball.vel);
        double bBallSpeed = phylib_length((*b)->obj.rolling_ball.vel);

        // check if either ball a or ball b speed is greater than PHYLIB_VEL_EPSILON
        if (aBallSpeed > PHYLIB_VEL_EPSILON) {
            (*a)->obj.rolling_ball.acc.x = (-(*a)->obj.rolling_ball.vel.x / aBallSpeed) * PHYLIB_DRAG;
            (*a)->obj.rolling_ball.acc.y = (-(*a)->obj.rolling_ball.vel.y / aBallSpeed) * PHYLIB_DRAG;
        }

        if (bBallSpeed > PHYLIB_VEL_EPSILON) {
            (*b)->obj.rolling_ball.acc.x = (-(*b)->obj.rolling_ball.vel.x / bBallSpeed) * PHYLIB_DRAG;
            (*b)->obj.rolling_ball.acc.y = (-(*b)->obj.rolling_ball.vel.y / bBallSpeed) * PHYLIB_DRAG;
        }
    }
}

unsigned char phylib_rolling( phylib_table *t ) {

    unsigned char rollingCount = 0;

    // iterate over every object on the table and if its not null and its a rolling ball then increment the count
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        if (t->object[i] != NULL && t->object[i]->type == PHYLIB_ROLLING_BALL) {
            rollingCount++;
        }
    }
    return rollingCount;
}

phylib_table *phylib_segment( phylib_table *table ) {

    int movingBalls;
    double time;
    // double runningTime = 0.0;

    movingBalls = phylib_rolling(table);

    if (movingBalls == 0) {
        return NULL;
    }
    
    // else create a copy of the table
    phylib_table *tableCopy = phylib_copy_table(table);

    // comment 
    for (time = PHYLIB_SIM_RATE; time <= PHYLIB_MAX_TIME; time = time + PHYLIB_SIM_RATE) {
    
        // iterate over every object on the table and roll them
        for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
            // if the object is not null, and is a rolling ball then apply the roll function to that ball
            if (tableCopy->object[i] != NULL && tableCopy->object[i]->type == PHYLIB_ROLLING_BALL) {
                phylib_roll(tableCopy->object[i], table->object[i], time);
            }
        }
        tableCopy->time = table->time + time;

        // then iterate over every object on the table again to check for collisions
        for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
            if (tableCopy->object[i] != NULL && tableCopy->object[i]->type == PHYLIB_ROLLING_BALL) {
                // check for collisions with other objects on the table
                // if an object is not null, is not itself, and has a distance of less than 0.0 then apply the bounce function
                for (int j = 0; j < PHYLIB_MAX_OBJECTS; j++) {
                    if (i != j && tableCopy->object[j] != NULL && phylib_distance(tableCopy->object[i], tableCopy->object[j]) < 0.0) {
                        phylib_bounce(&(tableCopy->object[i]), &(tableCopy->object[j]));
                        return tableCopy;
                    }
                }

                // check if the ball is stopped, if stopped then return the table 
                if (phylib_stopped(tableCopy->object[i])) {
                    return tableCopy;
                }
            }
        }
    }
    // phylib_free_table(table);

    // if the max time (PHYLIB_MAX_TIME) is reached then return the table
    return tableCopy;
}

char *phylib_object_string( phylib_object *object ) {
    
    static char string[80];
    if (object==NULL) {
        snprintf( string, 80, "NULL;" );
        return string;
    }

    switch (object->type) {
        case PHYLIB_STILL_BALL:
            snprintf( string, 80,
            "STILL_BALL (%d,%6.1lf,%6.1lf)",
            object->obj.still_ball.number,
            object->obj.still_ball.pos.x,
            object->obj.still_ball.pos.y );
        break;

        case PHYLIB_ROLLING_BALL:
            snprintf( string, 80,
            "ROLLING_BALL (%d,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf)",
            object->obj.rolling_ball.number,
            object->obj.rolling_ball.pos.x,
            object->obj.rolling_ball.pos.y,
            object->obj.rolling_ball.vel.x,
            object->obj.rolling_ball.vel.y,
            object->obj.rolling_ball.acc.x,
            object->obj.rolling_ball.acc.y );
        break;

        case PHYLIB_HOLE:
            snprintf( string, 80,
            "HOLE (%6.1lf,%6.1lf)",
            object->obj.hole.pos.x,
            object->obj.hole.pos.y );
        break;

        case PHYLIB_HCUSHION:
            snprintf( string, 80,
            "HCUSHION (%6.1lf)",
            object->obj.hcushion.y );
        break;

        case PHYLIB_VCUSHION:
            snprintf( string, 80,
            "VCUSHION (%6.1lf)",
            object->obj.vcushion.x );
        break;
    }
    return string;
}

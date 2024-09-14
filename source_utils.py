# #author: jumail-j
# #date: 2024-08-29

import obspython as obs
import re

def create_browser_source(source_name, url, width, height, scale_factor, pos_x, pos_y):
    # Check if the source already exists
    source = obs.obs_get_source_by_name(source_name)

    if source is None:
        # Create settings for the browser source
        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "url", url)
        obs.obs_data_set_int(settings, "width", width)
        obs.obs_data_set_int(settings, "height", height)

        # Create the browser source
        source = obs.obs_source_create("browser_source", source_name, settings, None)

        # Get the current scene
        current_scene = obs.obs_frontend_get_current_scene()
        scene = obs.obs_scene_from_source(current_scene)

        # Check if the group (scene) named "twitch-browsers" exists
        group_source = obs.obs_get_source_by_name("twitch-browsers")
        if group_source is None:
            # Create a new scene (group)
            group_settings = obs.obs_data_create()
            obs.obs_data_set_string(group_settings, "name", "twitch-browsers")
            group_source = obs.obs_source_create("scene", "twitch-browsers", group_settings, None)
            obs.obs_scene_add(scene, group_source)
            obs.obs_data_release(group_settings)

        # Get the group (scene) and add the new source to it
        group_scene = obs.obs_scene_from_source(group_source)
        scene_item = obs.obs_scene_add(group_scene, source)

        # Set the position of the source
        position_vec = obs.vec2()
        position_vec.x = pos_x
        position_vec.y = pos_y
        obs.obs_sceneitem_set_pos(scene_item, position_vec)

        # Scale the source down to a smaller size
        scale_vec = obs.vec2()
        scale_vec.x = scale_factor
        scale_vec.y = scale_factor
        obs.obs_sceneitem_set_scale(scene_item, scale_vec)

        # Release scene and source references
        obs.obs_data_release(settings)
        obs.obs_source_release(source)
        obs.obs_source_release(current_scene)
        obs.obs_source_release(group_source)
    else:
        print(f"Source '{source_name}' already exists.")


def add_source_below(target_source_name, new_source_name, url, width, height, scale_factor, pos_x, pos_y):
    # Get the 'twitch-browsers' scene
    twitch_scene = obs.obs_get_source_by_name("twitch-browsers")
    if not twitch_scene:
        print("Failed to get the 'twitch-browsers' scene!")
        return

    scene = obs.obs_scene_from_source(twitch_scene)
    if not scene:
        print("Failed to get the scene from 'twitch-browsers' source!")
        obs.obs_source_release(twitch_scene)
        return

    # Get the scene items (sources) in the 'twitch-browsers' scene
    scene_items = obs.obs_scene_enum_items(scene)

    target_scene_item = None

    # Find the target source in the 'twitch-browsers' scene
    for scene_item in scene_items:
        source = obs.obs_sceneitem_get_source(scene_item)
        name = obs.obs_source_get_name(source)

        # Check if this is the target source we want to add another source under
        if name == target_source_name:
            target_scene_item = scene_item
            break

    if target_scene_item:
        # Create settings for the new browser source
        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "url", url)
        obs.obs_data_set_int(settings, "width", width)
        obs.obs_data_set_int(settings, "height", height)

        # Create the new browser source
        new_source = obs.obs_source_create("browser_source", new_source_name, settings, None)

        if new_source:
            # Add the new source to the 'twitch-browsers' scene
            scene_item = obs.obs_scene_add(scene, new_source)
            if scene_item:
                # Set the position of the source
                position_vec = obs.vec2()
                position_vec.x = pos_x
                position_vec.y = pos_y
                obs.obs_sceneitem_set_pos(scene_item, position_vec)

                # Apply scaling
                scale_vec = obs.vec2()
                scale_vec.x = scale_factor
                scale_vec.y = scale_factor
                obs.obs_sceneitem_set_scale(scene_item, scale_vec)

                # Move the new source below the target source
                # Correct method usage
                obs.obs_sceneitem_set_order(scene_item, obs.OBS_ORDER_MOVE_DOWN)
            else:
                print("Failed to add new source to the 'twitch-browsers' scene!")

            # Release the new source object to avoid memory leaks
            obs.obs_source_release(new_source)
        else:
            print("Failed to create new source!")

        # Release settings object
        obs.obs_data_release(settings)
    else:
        print("Target source not found in 'twitch-browsers' scene!")

    # Release the scene items and 'twitch-browsers' scene objects
    obs.sceneitem_list_release(scene_items)
    obs.obs_source_release(twitch_scene)


def show_source(source_name):
    # Get the current scene
    current_scene = obs.obs_frontend_get_current_scene()
    scene = obs.obs_scene_from_source(current_scene)

    if scene is not None:
        # Find the source item within the scene
        scene_item = obs.obs_scene_find_source(scene, source_name)
        if scene_item is not None:
            # Set the source item to be visible
            obs.obs_sceneitem_set_visible(scene_item, True)
            print(f"Source '{source_name}' is now visible.")
        else:
            print(f"Source '{source_name}' not found in the current scene.")
    else:
        print("No active scene found.")

    # Release the scene reference
    obs.obs_source_release(current_scene)


def delete_source(source_name):
        # Get the 'twitch-browsers' scene
    twitch_scene = obs.obs_get_source_by_name("twitch-browsers")
    if not twitch_scene:
        print("Failed to get the 'twitch-browsers' scene!")
        return

    scene = obs.obs_scene_from_source(twitch_scene)
    if not scene:
        print("Failed to get the scene from 'twitch-browsers' source!")
        obs.obs_source_release(twitch_scene)
        return

    # Get the scene items (sources) in the 'twitch-browsers' scene
    scene_items = obs.obs_scene_enum_items(scene)

    scene_item_to_delete = None

    # Find the source within the 'twitch-browsers' scene
    for scene_item in scene_items:
        source = obs.obs_sceneitem_get_source(scene_item)
        name = obs.obs_source_get_name(source)

        if name == source_name:
            scene_item_to_delete = scene_item
            break

    if scene_item_to_delete:
        # Remove the source from the scene
        obs.obs_sceneitem_remove(scene_item_to_delete)
        print(f"Source '{source_name}' has been deleted from 'twitch-browsers' scene.")
    else:
        print(f"Source '{source_name}' not found in the 'twitch-browsers' scene.")

    # Release the scene items and 'twitch-browsers' scene objects
    obs.sceneitem_list_release(scene_items)
    obs.obs_source_release(twitch_scene)